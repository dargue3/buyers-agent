def chat_loop(query_engine):
    """Run the interactive chat loop with the loaded document"""
    print("\nPDF loaded! You can now chat with your document.")
    print("Type 'quit' to exit the chat.")
    
    while True:
        question = input("\nYour question: ")
        if question.lower() in ['quit', 'exit', 'q']:
            break
            
        response = query_engine.query(question)
        print("\nAnswer:", response.response)
