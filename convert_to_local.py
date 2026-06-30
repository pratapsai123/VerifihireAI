"""
Script to convert domain URLs to localhost URLs
Run this for local development
"""

from convert_to_domain import convert_files

if __name__ == "__main__":
    convert_files(to_local=True)
    print("\nConversion complete!")
