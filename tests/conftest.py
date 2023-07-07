import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--live-session",
        action="store_true",
        default=False,
        help="Use live session instead of stored HTML test files.",
    )  # "store_true" returns True if argument is present, else False


@pytest.fixture
def use_live_session(request):
    return request.config.getoption("--live-session")
