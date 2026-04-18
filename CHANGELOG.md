## [1.2.1](https://github.com/JeremieLitzler/linkprobe/compare/v1.2.0...v1.2.1) (2026-04-18)

### Bug Fixes

- **normalizer:** add percent-encoding spaces in URLs ([#40](https://github.com/JeremieLitzler/linkprobe/issues/40)) ([85eeb18](https://github.com/JeremieLitzler/linkprobe/commit/85eeb180b4a5511591deba4893726e28c3fa9720))

## [1.2.0](https://github.com/JeremieLitzler/linkprobe/compare/v1.1.0...v1.2.0) (2026-04-17)

### Features

- **emailer:** update email subject to broken link(s) to review format ([1e57266](https://github.com/JeremieLitzler/linkprobe/commit/1e57266f232d4346be95ef19df67cef5393ccd83))
- **filter:** add --keep-status-codes parameter to filter report output closes [#39](https://github.com/JeremieLitzler/linkprobe/issues/39) ([423f1d2](https://github.com/JeremieLitzler/linkprobe/commit/423f1d2e56598d958ee9c70ef6ea98766d4b3c32))
- **specs:** record specs for issue-39 add filter to keep status code in report ([616aeee](https://github.com/JeremieLitzler/linkprobe/commit/616aeeec6048ae79a7a094d1c82a8367cdf00d1a))

### Others

- **filter:** add and update tests for --keep-status-codes and status filter closes [#39](https://github.com/JeremieLitzler/linkprobe/issues/39) ([01b20df](https://github.com/JeremieLitzler/linkprobe/commit/01b20dfcae87105f4a6919ed2596f4675ba5bada))
- **filter:** clarify \_tally_excluded intent with comment ([48dd65c](https://github.com/JeremieLitzler/linkprobe/commit/48dd65cf3c4991cf09f992ab1806c0fd668277ef))

## [1.1.0](https://github.com/JeremieLitzler/linkprobe/compare/v1.0.0...v1.1.0) (2026-02-26)

### Features

- add --include-3xx-status-code flag to email notifications [#35](https://github.com/JeremieLitzler/linkprobe/issues/35) ([#36](https://github.com/JeremieLitzler/linkprobe/issues/36)) ([26aaead](https://github.com/JeremieLitzler/linkprobe/commit/26aaeaddb76326f180788fb7dfeb077fda4a4939))

## 1.0.0 (2026-02-25)

### Features

- add GitHub Actions CI workflow to run tests on PRs ([9f0bb7b](https://github.com/JeremieLitzler/linkprobe/commit/9f0bb7bb0de1d87971f27919e273dd5f93ad5d4e))
- add live terminal feedback during crawl and status-check phases ([d1e5dbf](https://github.com/JeremieLitzler/linkprobe/commit/d1e5dbffcb8784585550308093dac8cdf24ce9ef))
- add multi-agent pipeline setup ([fe06f02](https://github.com/JeremieLitzler/linkprobe/commit/fe06f02ead3b194a7c699f52716b7de3c1d9ab80))
- add Python dead link checker CLI tool ([ba608ea](https://github.com/JeremieLitzler/linkprobe/commit/ba608eae23f438f59ba3105ff1cc698a58a8ef62))
- **email:** use Resend Python SDK for email notifications ([79c9a44](https://github.com/JeremieLitzler/linkprobe/commit/79c9a4420ab24e4921aa782381ee8ad4ba4fb063))
- enable semantic versioning [#28](https://github.com/JeremieLitzler/linkprobe/issues/28) ([26e432b](https://github.com/JeremieLitzler/linkprobe/commit/26e432ba9004a181e33b2f5871e20515c20025ad))
- implement [#10](https://github.com/JeremieLitzler/linkprobe/issues/10) ([6eadcae](https://github.com/JeremieLitzler/linkprobe/commit/6eadcae9b5cc2bf8f6eb8faeed31dce5ad05a9be))
- **reporter:** add per-scan Markdown summary for issue [#8](https://github.com/JeremieLitzler/linkprobe/issues/8) ([14abce7](https://github.com/JeremieLitzler/linkprobe/commit/14abce752023dc8fa3faabe75bfa6f38630c1285))

### Bug Fixes

- add missing workflow [#28](https://github.com/JeremieLitzler/linkprobe/issues/28) ([836e0f8](https://github.com/JeremieLitzler/linkprobe/commit/836e0f8acfb22b2c74b693b3f5f4679c14e00f8d))
- **tests:** split test_checker.py into per-module test files ([be1c76f](https://github.com/JeremieLitzler/linkprobe/commit/be1c76f026bb4c0678ddbebc96dbf212a0b8f8ee))
- update arry of URL to check ([6600171](https://github.com/JeremieLitzler/linkprobe/commit/6600171cec56482ebd3f39840d0f8a976c3b93f8))

### Others

- add Claude Code local settings with sample site permission ([5a0bcf8](https://github.com/JeremieLitzler/linkprobe/commit/5a0bcf85bf06eda66b984bc82026bc97a3dd65a5))
- add commands and architecture sections to CLAUDE.md ([34e3a71](https://github.com/JeremieLitzler/linkprobe/commit/34e3a7129e9d2d49264d36f2ad659bec32e68619))
- add expected CSV output for sample website ([baafb92](https://github.com/JeremieLitzler/linkprobe/commit/baafb92b72d30065d143617a70d0220c40c8f5e0))
- add intermediate git commits after specs and coding steps ([1563253](https://github.com/JeremieLitzler/linkprobe/commit/15632532421cfcae03d30a4ea187c9821a48b01f))
- add rename test_web_parser.py ([67056c2](https://github.com/JeremieLitzler/linkprobe/commit/67056c231e55f395a16a62c3b76771edf1e888b1))
- add resend website URL to README ([6355f84](https://github.com/JeremieLitzler/linkprobe/commit/6355f84b8317e06b1cc7e127bcbc9067ce9f73f3))
- add sample website for testing ([385610f](https://github.com/JeremieLitzler/linkprobe/commit/385610f8aca91d0e95d613a9200f9f9a1f15c43a))
- add SDK-based email notification tests ([9183ee5](https://github.com/JeremieLitzler/linkprobe/commit/9183ee5669289a8f7a8490f14919cd22565f8bdb))
- add summary for issue [#10](https://github.com/JeremieLitzler/linkprobe/issues/10) ([055bc07](https://github.com/JeremieLitzler/linkprobe/commit/055bc07e79bf410274e01d50a5c4c23251ddb60f))
- add unit test and manual test commands to README ([0a7b744](https://github.com/JeremieLitzler/linkprobe/commit/0a7b744d5314bc561c1f8091130ae4e122cc79be))
- add usage instructions to README ([0a66701](https://github.com/JeremieLitzler/linkprobe/commit/0a66701a5a6993ea02afeba4638d819cb82657ec))
- fix versioning agent timing and tester agent timeout in pipeline ([96f8f17](https://github.com/JeremieLitzler/linkprobe/commit/96f8f17598ff1f77cbdc07dba863a27440ff0acb))
- move argument parser tests to test_argument_parser.py ([5c98576](https://github.com/JeremieLitzler/linkprobe/commit/5c98576c8f4562ad694d6f161d39e12c02757965))
- move source files into src/ and update all references ([ee40947](https://github.com/JeremieLitzler/linkprobe/commit/ee409473620e7152594b4a6e0c612eb702d9b2c5))
- record specs for Resend SDK migration ([#10](https://github.com/JeremieLitzler/linkprobe/issues/10) follow-up) ([f7d22f8](https://github.com/JeremieLitzler/linkprobe/commit/f7d22f8483f8446d2b50e77bdca66441b085121a))
- remove 'Manual Testing' redondant + .gitignore ([bfcdb0c](https://github.com/JeremieLitzler/linkprobe/commit/bfcdb0cc9d5f45c50a28c7053b72db37cdcd9cc6))
- rename .agents to .agents-output and prompts to .agents-brain ([1df9982](https://github.com/JeremieLitzler/linkprobe/commit/1df998229f4ad99b56b539d4840f6b4ae3a3c348))
- rewrite README with structured sections and pipeline overview ([b6bb26c](https://github.com/JeremieLitzler/linkprobe/commit/b6bb26cf377fe8ee860728e099c1ace4968e24f5))
- shift specs agent to business behaviour and add coder rules ([917207d](https://github.com/JeremieLitzler/linkprobe/commit/917207d256f7a414b66a3d847e0b3d4610e41650))
- **specs:** record specs for Issue [#18](https://github.com/JeremieLitzler/linkprobe/issues/18) — agentic workflow updates ([72398e6](https://github.com/JeremieLitzler/linkprobe/commit/72398e6d245e2db7e58772b7441844b89beaa9cd))
- tweak CLAUDE.md and orchestrator ([ec4f0dd](https://github.com/JeremieLitzler/linkprobe/commit/ec4f0dd62138532758a1a200ec885b4e84cf8acb))
- update README with installation, new flags, and email notification usage ([e0e0a40](https://github.com/JeremieLitzler/linkprobe/commit/e0e0a406fa1d70b72dfaea17efe067fcb95d12ec))
- update sub agents with additional instructions ([29f5b6f](https://github.com/JeremieLitzler/linkprobe/commit/29f5b6f4209e6fae429c7b0ab5b4028ae9dd55fe))
- verify agent prompt updates for Issue [#18](https://github.com/JeremieLitzler/linkprobe/issues/18) ([cd04fe8](https://github.com/JeremieLitzler/linkprobe/commit/cd04fe8f76b3a2f11ae5adb9d7c4a9bffbaa9815))
