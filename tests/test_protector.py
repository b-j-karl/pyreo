from pyreo.protector import protect, restore


class TestProtect:
    def test_protects_double_quoted_string(self):
        source = 'tā("kia ora")'
        protected, tokens = protect(source)
        assert "kia ora" not in protected
        assert "tā(" in protected

    def test_protects_single_quoted_string(self):
        source = "tā('kia ora')"
        protected, tokens = protect(source)
        assert "kia ora" not in protected

    def test_protects_triple_quoted_string(self):
        source = 'tā("""kia ora\nki a koe""")'
        protected, tokens = protect(source)
        assert "kia ora" not in protected

    def test_protects_hash_comments(self):
        source = "x = 5  # mena this is a comment with keywords"
        protected, tokens = protect(source)
        assert "mena" not in protected
        assert "x = 5" in protected

    def test_protects_fstring(self):
        source = 'tā(f"ko {ingoa} tōku ingoa")'
        protected, tokens = protect(source)
        assert "tōku ingoa" not in protected

    def test_preserves_code_outside_strings(self):
        source = 'mena x == 5:\n    tā("ae")'
        protected, tokens = protect(source)
        assert "mena" in protected

    def test_handles_empty_string(self):
        source = 'tā("")'
        protected, tokens = protect(source)
        restored = restore(protected, tokens)
        assert restored == source

    def test_handles_no_strings(self):
        source = "x = 5 + 3"
        protected, tokens = protect(source)
        assert protected == source
        assert tokens == {}


class TestRestore:
    def test_roundtrip_preserves_source(self):
        source = 'mena x > 0:\n    tā("x is positive")  # check\n    tā(\'done\')'
        protected, tokens = protect(source)
        restored = restore(protected, tokens)
        assert restored == source

    def test_roundtrip_with_multiple_strings(self):
        source = 'tā("one", "two", "three")'
        protected, tokens = protect(source)
        restored = restore(protected, tokens)
        assert restored == source

    def test_roundtrip_with_nested_quotes(self):
        source = """tā("she said 'kia ora'")"""
        protected, tokens = protect(source)
        restored = restore(protected, tokens)
        assert restored == source
