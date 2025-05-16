import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.rag import retrieve_studies, rag_analysis

if __name__ == '__main__':
    print(rag_analysis('sucralose'))