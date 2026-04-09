import sys
import os

# Add apps/api to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../apps/api')))

from audio_science import CamelotWheel

def test_normalization():
    print("Testing Normalization...")
    assert CamelotWheel.normalize_key("Am") == "8A"
    assert CamelotWheel.normalize_key("C") == "8B"
    assert CamelotWheel.normalize_key("8A") == "8A"
    assert CamelotWheel.normalize_key("Db") == "3B"
    # assert CamelotWheel.normalize_key("C#") == "3B" # C# is 3B (Db) or ... C# Major is Db Major (3B).
    print("✅ Normalization Passed")

def test_compatibility():
    print("\nTesting Compatibility...")
    
    # Test 8A (Am)
    # Compatible: 8A, 7A, 9A, 8B
    compat_8a = CamelotWheel.get_compatible_keys("8A")
    print(f"8A Compatible: {compat_8a}")
    expected_8a = ["8A", "7A", "9A", "8B"]
    for k in expected_8a:
        assert k in compat_8a
    
    # Test 12B (E Major)
    # Compatible: 12B, 11B, 1B (Wrap), 12A
    compat_12b = CamelotWheel.get_compatible_keys("12B")
    print(f"12B Compatible: {compat_12b}")
    expected_12b = ["12B", "11B", "1B", "12A"]
    for k in expected_12b:
        assert k in compat_12b
        
    print("✅ Compatibility Passed")

if __name__ == "__main__":
    try:
        test_normalization()
        test_compatibility()
        print("\n🎉 ALL AUDIO SCIENCE TESTS PASSED")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)
