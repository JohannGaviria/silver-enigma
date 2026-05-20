from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
import pytest
from faker import Faker

from src.modules.auth.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.exception import (
    ExpiredTokenException,
    InvalidAccessTokenPayloadException,
    InvalidTokenException,
)
from src.shared.domain.value_objects.access_token_input_vo import AccessTokenInputVO
from src.shared.domain.value_objects.access_token_payload_vo import AccessTokenPayloadVO
from src.shared.domain.value_objects.token_vo import TokenVO
from src.shared.infrastructure.outbound.pyjwt_token_outbound_adapter import (
    PyJWTTokenOutboundAdapter,
)


class TestPyJWTTokenOutboundAdapter:
    # ---------------------------------------------------------------------------
    # Method: _get_required_claim
    # ---------------------------------------------------------------------------
    def test_should_return_claim_value_when_claim_exists_in_payload(
        self, faker: Faker, token_outbound: PyJWTTokenOutboundAdapter
    ) -> None:
        """Test that the _get_required_claim method returns the claim value.

        when the claim exists in the payload.
        """
        payload = AccessTokenPayloadVO(
            jti=UUID(faker.uuid4()),
            sub=UUID(faker.uuid4()),
            role=UserRoleEnum.ADMIN,
            exp=faker.future_datetime(600, UTC),
        )

        result_key_jti = token_outbound._get_required_claim(payload.to_dict(), "jti")
        result_key_sub = token_outbound._get_required_claim(payload.to_dict(), "sub")
        result_key_role = token_outbound._get_required_claim(payload.to_dict(), "role")
        result_key_exp = token_outbound._get_required_claim(payload.to_dict(), "exp")

        assert result_key_jti == str(payload.jti)
        assert result_key_sub == str(payload.sub)
        assert result_key_role == payload.role.value
        assert result_key_exp == payload.exp

    def test_should_raise_exception_when_claim_does_not_exist_in_payload(
        self, faker: Faker, token_outbound: PyJWTTokenOutboundAdapter
    ) -> None:
        """Test that the _get_required_claim method raises an InvalidAccessTokenPayloadException.

        when the claim does not exist in the payload.
        """
        payload = AccessTokenPayloadVO(
            jti=UUID(faker.uuid4()),
            sub=UUID(faker.uuid4()),
            role=UserRoleEnum.ADMIN,
            exp=faker.future_datetime(600, UTC),
        )

        with pytest.raises(InvalidAccessTokenPayloadException):
            token_outbound._get_required_claim(payload.to_dict(), "user_id")

    def test_should_raise_exception_when_claim_value_is_none(
        self, token_outbound: PyJWTTokenOutboundAdapter
    ) -> None:
        """Test that the _get_required_claim method raises an InvalidAccessTokenPayloadException.

        when the claim value is None.
        """
        payload: dict[str, object] = {
            "sub": None,
        }

        with pytest.raises(InvalidAccessTokenPayloadException):
            token_outbound._get_required_claim(payload, "sub")

    # ---------------------------------------------------------------------------
    # Method: _generate
    # ---------------------------------------------------------------------------
    def test_should_generate_empty_token_when_no_payload_is_provided(
        self, token_outbound: PyJWTTokenOutboundAdapter
    ) -> None:
        """Test that the _generate method returns a valid empty token.

        when no payload is provided.
        """
        result = token_outbound._generate()

        decoded = jwt.decode(
            jwt=str(result),
            key=token_outbound.token_secret_key,
            algorithms=[token_outbound.token_algorithm],
        )

        assert isinstance(result, TokenVO)
        assert decoded == {}

    def test_should_generate_token_with_payload_when_input_is_provided(
        self, faker: Faker, token_outbound: PyJWTTokenOutboundAdapter
    ) -> None:
        """Test that the _generate method returns a token containing the expected payload claims.

        when an AccessTokenInputVO is provided.
        """
        input = AccessTokenInputVO.create(
            sub=UUID(faker.uuid4()), role=UserRoleEnum.ADMIN
        )

        result = token_outbound._generate(input)

        decoded = jwt.decode(
            jwt=str(result),
            key=token_outbound.token_secret_key,
            algorithms=[token_outbound.token_algorithm],
        )

        payload = AccessTokenPayloadVO(
            jti=UUID(decoded["jti"]),
            sub=UUID(decoded["sub"]),
            role=UserRoleEnum(decoded["role"]),
            exp=datetime.fromtimestamp(decoded["exp"], tz=UTC),
        )

        assert isinstance(result, TokenVO)
        assert str(payload.jti) == str(input.jti)
        assert str(payload.sub) == str(input.sub)
        assert payload.role == input.role
        assert payload.exp

    def test_should_set_expiration_claim_when_generating_access_token(
        self, faker: Faker, token_outbound: PyJWTTokenOutboundAdapter
    ) -> None:
        """Test that the _generate method sets the expiration.

        claim using the configured access token expiration time.
        """
        input = AccessTokenInputVO(
            jti=UUID(faker.uuid4()),
            sub=UUID(faker.uuid4()),
            role=UserRoleEnum.ADMIN,
        )

        before_generation = datetime.now(UTC)

        result = token_outbound._generate(input)

        after_generation = datetime.now(UTC)

        decoded = jwt.decode(
            jwt=str(result),
            key=token_outbound.token_secret_key,
            algorithms=[token_outbound.token_algorithm],
            options={"verify_exp": False},
        )

        expected_exp = int(
            (
                before_generation + timedelta(seconds=token_outbound.access_expires_in)
            ).timestamp()
        )

        current_exp = decoded["exp"]

        max_expected_exp = int(
            (
                after_generation + timedelta(seconds=token_outbound.access_expires_in)
            ).timestamp()
        )

        assert expected_exp <= current_exp <= max_expected_exp

    def test_should_include_required_claims_when_generating_token(
        self, faker: Faker, token_outbound: PyJWTTokenOutboundAdapter
    ) -> None:
        """Test that the _generate method includes all required claims in the generated token payload."""
        jti = UUID(faker.uuid4())
        sub = UUID(faker.uuid4())

        input = AccessTokenInputVO(
            jti=jti,
            sub=sub,
            role=UserRoleEnum.ADMIN,
        )

        result = token_outbound._generate(input)

        decoded = jwt.decode(
            str(result),
            token_outbound.token_secret_key,
            algorithms=[token_outbound.token_algorithm],
            options={"verify_exp": False},
        )

        assert decoded["jti"] == str(jti)
        assert decoded["sub"] == str(sub)
        assert decoded["role"] == UserRoleEnum.ADMIN.value
        assert "exp" in decoded

    # ---------------------------------------------------------------------------
    # Method: generate_access
    # ---------------------------------------------------------------------------

    def test_should_return_access_token_response_when_generating_access_token(
        self, faker: Faker, token_outbound: PyJWTTokenOutboundAdapter
    ) -> None:
        """Test that the generate_access method returns a valid access token response."""
        input = AccessTokenInputVO.create(
            sub=UUID(faker.uuid4()), role=UserRoleEnum.ADMIN
        )

        response = token_outbound.generate_access(input)

        assert isinstance(response.access_token, TokenVO)
        assert response.token_type == "Bearer"
        assert response.expires_in == token_outbound.access_expires_in

    # ---------------------------------------------------------------------------
    # Method: generate_refresh
    # ---------------------------------------------------------------------------

    def test_should_return_refresh_token_response_when_generating_refresh_token(
        self, token_outbound: PyJWTTokenOutboundAdapter
    ) -> None:
        """Test that the generate_refresh method returns a valid refresh token response."""
        response = token_outbound.generate_refresh()

        assert isinstance(response.refresh_token, TokenVO)
        assert response.expires_in == token_outbound.refresh_expires_in

    # ---------------------------------------------------------------------------
    # Method: decode
    # ---------------------------------------------------------------------------

    def test_should_return_payload_when_token_is_valid(
        self, faker: Faker, token_outbound: PyJWTTokenOutboundAdapter
    ) -> None:
        """Test that the decode method returns an AccessTokenPayloadVO when the token is valid."""
        jti = UUID(faker.uuid4())
        sub = UUID(faker.uuid4())

        exp = datetime.now(UTC) + timedelta(hours=1)

        token = jwt.encode(
            {
                "jti": str(jti),
                "sub": str(sub),
                "role": UserRoleEnum.ADMIN,
                "exp": exp,
            },
            token_outbound.token_secret_key,
            algorithm=token_outbound.token_algorithm,
        )

        result = token_outbound.decode(TokenVO(token))

        assert isinstance(result, AccessTokenPayloadVO)
        assert result.jti == jti
        assert result.sub == sub
        assert result.role == UserRoleEnum.ADMIN
        assert int(result.exp.timestamp()) == int(exp.timestamp())

    def test_should_raise_exception_when_token_has_expired(
        self, faker: Faker, token_outbound: PyJWTTokenOutboundAdapter
    ) -> None:
        """Test that the decode method raises an ExpiredTokenException when the token has expired."""
        token = jwt.encode(
            {
                "jti": faker.uuid4(),
                "sub": faker.uuid4(),
                "role": UserRoleEnum.ADMIN,
                "exp": datetime.now(UTC) - timedelta(hours=1),
            },
            token_outbound.token_secret_key,
            algorithm=token_outbound.token_algorithm,
        )

        with pytest.raises(ExpiredTokenException):
            token_outbound.decode(TokenVO(token))

    def test_should_raise_exception_when_token_is_invalid(
        self,
        token_outbound: PyJWTTokenOutboundAdapter,
    ) -> None:
        """Test that the decode method raises an InvalidTokenException.

        when the token is invalid.
        """
        invalid_token = TokenVO("invalid.token.value")

        with pytest.raises(InvalidTokenException):
            token_outbound.decode(invalid_token)

    def test_should_raise_exception_when_jti_claim_is_missing(
        self,
        faker: Faker,
        token_outbound: PyJWTTokenOutboundAdapter,
    ) -> None:
        """Test that the decode method raises an InvalidAccessTokenPayloadException.

        when the jti claim is missing.
        """
        token = jwt.encode(
            {
                "sub": faker.uuid4(),
                "role": UserRoleEnum.ADMIN.value,
                "exp": datetime.now(UTC) + timedelta(hours=1),
            },
            token_outbound.token_secret_key,
            algorithm=token_outbound.token_algorithm,
        )

        with pytest.raises(InvalidAccessTokenPayloadException):
            token_outbound.decode(TokenVO(token))

    def test_should_raise_exception_when_sub_claim_is_missing(
        self,
        faker: Faker,
        token_outbound: PyJWTTokenOutboundAdapter,
    ) -> None:
        """Test that the decode method raises an InvalidAccessTokenPayloadException.

        when the sub claim is missing.
        """
        token = jwt.encode(
            {
                "jti": faker.uuid4(),
                "role": UserRoleEnum.ADMIN.value,
                "exp": datetime.now(UTC) + timedelta(hours=1),
            },
            token_outbound.token_secret_key,
            algorithm=token_outbound.token_algorithm,
        )

        with pytest.raises(InvalidAccessTokenPayloadException):
            token_outbound.decode(TokenVO(token))

    def test_should_raise_exception_when_role_claim_is_missing(
        self,
        faker: Faker,
        token_outbound: PyJWTTokenOutboundAdapter,
    ) -> None:
        """Test that the decode method raises an InvalidAccessTokenPayloadException.

        when the role claim is missing.
        """
        token = jwt.encode(
            {
                "jti": faker.uuid4(),
                "sub": faker.uuid4(),
                "exp": datetime.now(UTC) + timedelta(hours=1),
            },
            token_outbound.token_secret_key,
            algorithm=token_outbound.token_algorithm,
        )

        with pytest.raises(InvalidAccessTokenPayloadException):
            token_outbound.decode(TokenVO(token))

    def test_should_raise_exception_when_exp_claim_is_missing(
        self,
        faker: Faker,
        token_outbound: PyJWTTokenOutboundAdapter,
    ) -> None:
        """Test that the decode method raises an InvalidAccessTokenPayloadException.

        when the exp claim is missing.
        """
        token = jwt.encode(
            {
                "jti": faker.uuid4(),
                "sub": faker.uuid4(),
                "role": UserRoleEnum.ADMIN.value,
            },
            token_outbound.token_secret_key,
            algorithm=token_outbound.token_algorithm,
        )

        with pytest.raises(InvalidAccessTokenPayloadException):
            token_outbound.decode(TokenVO(token))
