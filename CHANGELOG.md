## [1.3.1](https://github.com/JohannGaviria/silver-enigma/compare/v1.3.0...v1.3.1) (2026-05-25)


### Bug Fixes

* **auth:** update exception imports and test dependencies ([c659a5b](https://github.com/JohannGaviria/silver-enigma/commit/c659a5b22ed0881426a554377e66d704ebe80912))

# [1.3.0](https://github.com/JohannGaviria/silver-enigma/compare/v1.2.0...v1.3.0) (2026-05-25)


### Bug Fixes

* **config:** correct CORS_ALLOW_CREDENTIALS type to bool ([9d976c1](https://github.com/JohannGaviria/silver-enigma/commit/9d976c15e79b38854a17b46bff31b826dc2bb57a))
* **config:** correct CORS_ALLOW_CREDENTIALS type to bool ([698ef3f](https://github.com/JohannGaviria/silver-enigma/commit/698ef3f40218ff77f38ea223cd8d67ae3521faef))
* load environment variables from .env.test in conftest ([cd5dfa9](https://github.com/JohannGaviria/silver-enigma/commit/cd5dfa99bc3fab9da61ec58b0176f4226950d73e))
* load environment variables from .env.test in conftest ([78a7021](https://github.com/JohannGaviria/silver-enigma/commit/78a70211138f84b60bca36550c1b69809625631b))


### Features

* **auth:** implement authentication module ([2413162](https://github.com/JohannGaviria/silver-enigma/commit/241316236a51b8fb2bebf8b9ab636a190458f0d9))
* **auth:** implement first admin bootstrap flow with domain, use case, CLI and tests ([360d36f](https://github.com/JohannGaviria/silver-enigma/commit/360d36f90b306e7a3c2b14a646d6a8827adb2826))
* **auth:** implement logout endpoint ([1d4b30f](https://github.com/JohannGaviria/silver-enigma/commit/1d4b30fa190174f492b3ea7a56aabd8fe825ff3e))
* **auth:** implement refresh token rotation endpoint ([89734bf](https://github.com/JohannGaviria/silver-enigma/commit/89734bf746d623b8ace71711db9edd3aec7b7cac))
* **auth:** implement user authentication endpoint ([973ba24](https://github.com/JohannGaviria/silver-enigma/commit/973ba24654157a6452fa2c4688711e6571d3e2d6))
* **auth:** implement user registration by the admin endpoint ([bd859b4](https://github.com/JohannGaviria/silver-enigma/commit/bd859b47d357bb673408d7e2cabef43ff916bc84))
* **config:** enable CORS support for cross-origin requests ([7d0f803](https://github.com/JohannGaviria/silver-enigma/commit/7d0f803c179dfe67d916403ade2f0873658623b3))
* **config:** enable CORS support for cross-origin requests ([1189f39](https://github.com/JohannGaviria/silver-enigma/commit/1189f3921b70f13d5085144950883372a5a0bf1c))
* implement unit of work pattern for transaction management ([516c1e0](https://github.com/JohannGaviria/silver-enigma/commit/516c1e0b8c488ab93e845436dd4a5bc26b91478e))
* **shared:** add domain layer base classes ([672194b](https://github.com/JohannGaviria/silver-enigma/commit/672194be0da5b66ea9cc672c16b7b2aab5275c2b))
* **shared:** add domain layer base classes ([f88bc6c](https://github.com/JohannGaviria/silver-enigma/commit/f88bc6c3db8aa70112efee36f87a8e88b1266b88))
* **shared:** add standardized response schemas ([1ec7c2e](https://github.com/JohannGaviria/silver-enigma/commit/1ec7c2eb134a6b724e99356eda1371dd2a84208c))
* **shared:** add standardized response schemas ([5092bb7](https://github.com/JohannGaviria/silver-enigma/commit/5092bb7a11f4411a2d245ec646a1ff886884a027))
* **shared:** implement asynchronous database engine ([94cbd0a](https://github.com/JohannGaviria/silver-enigma/commit/94cbd0ad794f809c7e48362de2c0f9f1e7ff26e1))
* **shared:** implement structured logging outbound ports and adapters ([79843d8](https://github.com/JohannGaviria/silver-enigma/commit/79843d8361e3ba700159f34c1f413cbd1bc9bee9))
* **shared:** integrate Alembic for database migrations ([a6b5221](https://github.com/JohannGaviria/silver-enigma/commit/a6b52210689e650a42c6ebfefb2992ce4c9f3303))
* **shared:** integrate Alembic for database migrations ([4750344](https://github.com/JohannGaviria/silver-enigma/commit/4750344669044c2e214828cb6afc1a5ac1ad4c5a))

# [1.2.0](https://github.com/JohannGaviria/silver-enigma/compare/v1.1.0...v1.2.0) (2026-05-04)


### Features

* **auth:** bootstrap backend architecture with auth module, async infra, and transactional patterns ([80a5688](https://github.com/JohannGaviria/silver-enigma/commit/80a5688fd202dda33ada7ba791ffea43d0aeafb2))

# [1.1.0](https://github.com/JohannGaviria/silver-enigma/compare/v1.0.0...v1.1.0) (2026-04-23)


### Features

* **shared:** dd domain layer base classes and enable CORS support ([609d017](https://github.com/JohannGaviria/silver-enigma/commit/609d017dcd37d7069c603f2de8025099cc98e45d))

# 1.0.0 (2026-04-22)


### Features

* add logging configuration, Redis and database infrastructure, and health check endpoint ([fd0db74](https://github.com/JohannGaviria/silver-enigma/commit/fd0db74c26cde26f7f5816d38cb586573f988118))
* **api:** introduce health check endpoint for service monitoring ([79e7dd2](https://github.com/JohannGaviria/silver-enigma/commit/79e7dd242dac3a30902e994873bf6128ba3368bc))
* **api:** introduce health check endpoint for service monitoring ([3e31d42](https://github.com/JohannGaviria/silver-enigma/commit/3e31d42ae6d5fbf3e9b8d8824f6575ce473f8be7))
* **shared:** add redis cache and database connection infrastructure ([a3012d2](https://github.com/JohannGaviria/silver-enigma/commit/a3012d21fa2c11e012b90bef8dc4d74e1ae83459))
* **shared:** add redis cache and database connection infrastructure ([49db837](https://github.com/JohannGaviria/silver-enigma/commit/49db837c080b4a4c364f82b07538626a9f24267e))
* **shared:** implement structlog-based logging configuration ([35e3e6d](https://github.com/JohannGaviria/silver-enigma/commit/35e3e6de5b0e5bded0a9f3d0e256513127f39c8b))
* **shared:** implement structlog-based logging configuration ([be26bac](https://github.com/JohannGaviria/silver-enigma/commit/be26bacc5a8ea90b382fc5c4feec21d1583f4df2))
