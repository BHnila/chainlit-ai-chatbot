# Chainlit Application with Data Persistence

This project is a simple student assistant chatbot built with Chainlit. It also demonstrates how to implement data persistence using PostgreSQL as a custom data layer.

## Getting Started

To run the application, follow these steps:

1.  **Create `.env` file in root folder**
    
2.  **Add OpenAI API Key** 

	Add the `OPENAI_API_KEY` variable to the `.env` file.

	If you don't have an API key, follow the instructions [here](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key) to obtain one.
    
4.  **Run Docker Compose**
    
    Run `docker compose up --build` 
    
5.  **Access the Chainlit App**

    Open your web browser and navigate to [localhost:8000](http://localhost:8000).
    

The application is ready to use out of the box. There is no need to change any settings.

## Components

The application is composed of two Docker containers:

-   **chainlit_app**: The Chainlit web-based chatbot.
-   **postgres**: The PostgreSQL database for data persistence.

Once the Chainlit application starts successfully, you can log in using **any made-up credentials**, as the login system is a mockup for demonstration purposes.

## Data persistence

The conversation history management feature is currently a demo and is not fully functional. Further development of the `LocalStorageClient` class is required to ensure it works properly.

## Information Resources

For more information on setting up a Chainlit-based chatbot or data persistence in Chainlit web apps, check out the following resources:

-   [Chainlit Documentation](https://docs.chainlit.io/get-started/overview)
-   [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Disclaimer

This app is a demo implementation of Chainlit created as part of the FEIrag project by the AI Team at FEI STU. It is unofficial and does not reflect the views or opinions of FEI STU, Bratislava.

## License

This project is licensed under the MIT License. For more details, see the [LICENSE](LICENSE) file.
