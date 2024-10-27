import hashlib

def get_file_hash(file_path):
    """Generate a hash of the file contents"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()
    
def ask_user_for_file_path():
    default_path = "pdfs/disclosures.pdf"
    pdf_path = input(f"Enter the path to your PDF file (press Enter to use {default_path}): ").strip()
    if not pdf_path:
        pdf_path = default_path
    return pdf_path