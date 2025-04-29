# Nutrition Tracker Chatbot

A conversational chatbot that helps you track your nutrition and monitor your fitness journey.

## Features

- Log food items through natural language conversation
- Track nutrition information for each food entry
- Generate daily nutrition reports
- Analyze trends over time
- Filter and view historical nutrition data

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/nutrition-tracker.git
   cd nutrition-tracker
   ```

2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### Running the Application

Start the application:
```
python app.py
```

## Usage

Once the chatbot is running, you can:

- Tell it what you've eaten: "I had oatmeal with berries for breakfast"
- Request nutrition analysis: "analyze today" or "analyze yesterday"
- View your food log: "show today's entries" or "what did I eat today"
- Get help: "help" for a list of commands

## Project Structure

- `app.py`: Main entry point
- `src/`: Core application code
  - `chatbot/`: Handles user interactions
  - `api/`: OpenAI API integration
  - `database/`: Data storage and retrieval
  - `analytics/`: Nutrition analysis
- `utils/`: Helper functions
- `tests/`: Unit and integration tests
- `data/`: Local data storage

## Future Enhancements

- Web interface
- Mobile app integration
- Image recognition for food logging
- Customizable nutrition goals
- Meal planning recommendations

## License

MIT