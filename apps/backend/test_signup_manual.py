#!/usr/bin/env python3
"""Manual test script to verify signup endpoints work correctly."""

import requests


# Test admin signup endpoint
def test_admin_signup():
    url = "http://localhost:8000/signup/admin"
    admin_data = {
        "name": "Test Administrator",
        "email": "test.admin@example.com",
        "department": "IT Testing",
        "role": "admin",
        "password": "SecurePassword123!",
    }

    try:
        response = requests.post(url, json=admin_data, timeout=10)
        print(f"Admin Signup Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print("✅ Admin signup successful!")
            print(f"User ID: {data['user']['id']}")
            print(f"User Type: {data['user']['user_type']}")
            print(f"Admin ID: {data['admin']['id']}")
            print(f"Admin Name: {data['admin']['name']}")
            print(f"Admin Email: {data['admin']['email']}")
            return True
        else:
            print(f"❌ Admin signup failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing admin signup: {e}")
        return False


# Test attorney signup endpoint
def test_attorney_signup():
    url = "http://localhost:8000/signup/attorney"
    attorney_data = {
        "name": "Test Attorney",
        "phone_number": "+15551234567",
        "email": "test.attorney@example.com",
        "zip_code": "12345",
        "state": "CA",
        "password": "SecurePassword123!",
    }

    try:
        response = requests.post(url, json=attorney_data, timeout=10)
        print(f"Attorney Signup Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print("✅ Attorney signup successful!")
            print(f"User ID: {data['user']['id']}")
            print(f"User Type: {data['user']['user_type']}")
            print(f"Attorney ID: {data['attorney']['id']}")
            print(f"Attorney Name: {data['attorney']['name']}")
            return True
        else:
            print(f"❌ Attorney signup failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing attorney signup: {e}")
        return False


# Test client signup endpoint
def test_client_signup():
    url = "http://localhost:8000/signup/client"
    client_data = {
        "first_name": "Test",
        "last_name": "Client",
        "country_of_birth": "United States",
        "birth_date": "1990-01-01",
        "password": "SecurePassword123!",
    }

    try:
        response = requests.post(url, json=client_data, timeout=10)
        print(f"Client Signup Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print("✅ Client signup successful!")
            print(f"User ID: {data['user']['id']}")
            print(f"User Type: {data['user']['user_type']}")
            print(f"Client ID: {data['client']['id']}")
            print(f"Client Name: {data['client']['first_name']} {data['client']['last_name']}")
            return True
        else:
            print(f"❌ Client signup failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing client signup: {e}")
        return False


# Test cross-endpoint email uniqueness
def test_email_uniqueness():
    shared_email = "shared.test@example.com"

    # Create attorney first
    attorney_url = "http://localhost:8000/signup/attorney"
    attorney_data = {
        "name": "First User",
        "phone_number": "+15551234567",
        "email": shared_email,
        "zip_code": "12345",
        "state": "CA",
        "password": "SecurePassword123!",
    }

    # Create admin with same email
    admin_url = "http://localhost:8000/signup/admin"
    admin_data = {
        "name": "Second User",
        "email": shared_email,
        "department": "IT",
        "role": "admin",
        "password": "SecurePassword123!",
    }

    try:
        # First signup should succeed
        response1 = requests.post(attorney_url, json=attorney_data, timeout=10)
        print(f"First signup (attorney) status: {response1.status_code}")

        # Second signup should fail
        response2 = requests.post(admin_url, json=admin_data, timeout=10)
        print(f"Second signup (admin) status: {response2.status_code}")

        if response1.status_code == 201 and response2.status_code == 400:
            print("✅ Email uniqueness test passed!")
            return True
        else:
            print("❌ Email uniqueness test failed!")
            print(f"Response 2 error: {response2.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing email uniqueness: {e}")
        return False


def main():
    print("🧪 Testing Three-Router Signup Architecture\n")

    tests = [
        ("Admin Signup", test_admin_signup),
        ("Attorney Signup", test_attorney_signup),
        ("Client Signup", test_client_signup),
        ("Email Uniqueness", test_email_uniqueness),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"--- Running {test_name} Test ---")
        result = test_func()
        results.append((test_name, result))
        print()

    print("📊 Test Results Summary:")
    print("=" * 40)
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nTotal: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n🎉 All tests passed! Three-router architecture is working correctly!")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please check the implementation.")


if __name__ == "__main__":
    main()
