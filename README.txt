    RankWise MCQ Arena is a full stack web application that generates intelligent multiple choice questions dynamically and evaluates student performance with real time ranking analytics. Users select their class, subject, and difficulty level. An AI powered engine generates 
    concept focused MCQs. Students attempt the quiz, submit answers, and instantly receive scores with detailed explanations for incorrect responses.

    The project also features a live leaderboard system. Student scores are stored with class information. The leaderboard ranks classes based on average scores and highlights the top three students in each class. This creates a competitive and engaging learning environment.

    The backend is built with Flask. The frontend uses HTML, CSS, and JavaScript. Data is stored in a JSON file for simplicity, with protection against duplicate or empty submissions. The structure is modular and easy to extend with databases and authentication later.
    
    -->Features

    • AI generated MCQs based on class, subject, and difficulty
    • Instant scoring and detailed explanations
    • Student name based score tracking
    • Class wise average ranking
    • Top three students per class
    • Persistent leaderboard storage
    • Clean and responsive user interface

    -->Tech Stack

        Frontend: HTML, CSS, JavaScript
        Backend: Python, Flask
        AI Engine: GROQ API
        Storage: JSON file

    -Prerequisites

    • Python 3.9 or above
    • A GROQ API key

    -->GROQ API Key Setup

    Do not use someone else’s API key. Create your own.

    1.Create a GROQ account

    2.Generate an API key

    3.Store it as an environment variable

    -->On Windows:
        set GROQ_API_KEY=your_api_key_here

    -On Mac or Linux:
        export GROQ_API_KEY=your_api_key_here

    -->Installation and Setup:

    --Open terminal or command prompt.

    -Navigate to project folder:
        cd <full path of project folder>

    -Create virtual environment:
        python -m venv venv

    -Activate virtual environment.
     Windows:
        venv\Scripts\activate

    Mac or Linux:
        source venv/bin/activate

    -Install required packages:
        pip install -r requirements.txt

    ->Running the Project:

    --Start the Flask server:
        python app.py

    --Open your browser and go to:
        http://127.0.0.1:5000

    Enter your name, choose class, subject, difficulty.
    Generate questions, attempt quiz, submit answers.
    View leaderboard to see rankings.