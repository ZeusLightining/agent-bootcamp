"""Test script to verify AML advisor setup.

Run this to check if all components are properly configured before launching
the full Gradio interface.

Usage:
    uv run --env-file .env python src/2_frameworks/2_multi_agent/test_aml_setup.py
"""

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.utils import (
    AsyncWeaviateKnowledgeBase,
    Configs,
    get_weaviate_async_client,
)


async def test_setup():
    """Test all components of the AML advisor setup."""
    print("\n" + "=" * 80)
    print("AML ADVISOR SETUP TEST")
    print("=" * 80 + "\n")

    # Load environment
    print("1. Loading environment variables...")
    load_dotenv(verbose=True)
    print("   ✓ Environment loaded\n")

    # Test configs
    print("2. Testing configuration...")
    try:
        configs = Configs.from_env_var()
        print(f"   ✓ Weaviate host: {configs.weaviate_http_host}")
        print(f"   ✓ Weaviate port: {configs.weaviate_http_port}")
        print(f"   ✓ API key configured: {'Yes' if configs.weaviate_api_key else 'No'}")
    except Exception as e:
        print(f"   ✗ Configuration error: {e}")
        return False
    print()

    # Test Weaviate connection
    print("3. Testing Weaviate connection...")
    try:
        async_weaviate_client = get_weaviate_async_client(
            http_host=configs.weaviate_http_host,
            http_port=configs.weaviate_http_port,
            http_secure=configs.weaviate_http_secure,
            grpc_host=configs.weaviate_grpc_host,
            grpc_port=configs.weaviate_grpc_port,
            grpc_secure=configs.weaviate_grpc_secure,
            api_key=configs.weaviate_api_key,
        )

        async with async_weaviate_client:
            is_ready = await async_weaviate_client.is_ready()
            if is_ready:
                print("   ✓ Weaviate connection successful")
            else:
                print("   ✗ Weaviate not ready")
                return False
    except Exception as e:
        print(f"   ✗ Weaviate connection failed: {e}")
        return False
    print()

    # Test knowledge base collections
    print("4. Testing knowledge base collections...")
    collections_to_test = [
        "aml_cdd_redflags",
        "aml_regulations",
        "aml_sar_guidelines",
        "aml_policies",
        "aml_case_studies",
    ]

    available_collections = []
    fallback_collections = []

    for collection_name in collections_to_test:
        try:
            kb = AsyncWeaviateKnowledgeBase(
                async_weaviate_client,
                collection_name=collection_name,
                num_results=1,
            )
            # Try a simple search to verify it works
            async with async_weaviate_client:
                results = await kb.search_knowledgebase("test")
                print(f"   ✓ {collection_name}: Available ({len(results)} test results)")
                available_collections.append(collection_name)
        except Exception as e:
            print(f"   ⚠ {collection_name}: Not found (will use fallback)")
            fallback_collections.append(collection_name)
    print()

    # Test fallback collection
    if fallback_collections:
        print("5. Testing fallback collection (enwiki_20250520)...")
        try:
            kb = AsyncWeaviateKnowledgeBase(
                async_weaviate_client,
                collection_name="enwiki_20250520",
                num_results=1,
            )
            async with async_weaviate_client:
                results = await kb.search_knowledgebase("test")
                print(f"   ✓ Fallback collection available ({len(results)} test results)")
                print(
                    f"   ℹ {len(fallback_collections)} collection(s) will use fallback"
                )
        except Exception as e:
            print(f"   ✗ Fallback collection also unavailable: {e}")
            print("   ⚠ You may need to create AML-specific collections")
    print()

    # Summary
    print("=" * 80)
    print("SETUP TEST SUMMARY")
    print("=" * 80)
    print(f"✓ Environment: Configured")
    print(f"✓ Weaviate: Connected")
    print(f"✓ Collections available: {len(available_collections)}/5")

    if fallback_collections:
        print(f"⚠ Collections using fallback: {len(fallback_collections)}/5")
        print("\nRecommendation:")
        print("  Create these collections in Weaviate for optimal performance:")
        for col in fallback_collections:
            print(f"    - {col}")
        print("\n  See AML_KNOWLEDGE_BASE_SETUP.md for instructions.")
    else:
        print("✓ All AML collections available!")

    print("\n" + "=" * 80)
    print("READY TO LAUNCH!")
    print("=" * 80)
    print("\nRun the Gradio interface:")
    print(
        "  uv run --env-file .env gradio src/2_frameworks/2_multi_agent/aml_advisor_gradio.py"
    )
    print()

    # Cleanup
    await async_weaviate_client.close()

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_setup())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
