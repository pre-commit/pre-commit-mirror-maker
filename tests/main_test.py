from pre_commit_mirror_maker.main import main


def test_main():
    ret = main([])
    assert ret == 0
