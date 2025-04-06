# ML Practice Platform

A LeetCode-style platform for learning and practicing Machine Learning problems. This platform helps users learn ML concepts through hands-on coding challenges.

## Features

- Structured learning path from basics to advanced ML concepts
- Interactive coding environment
- Problem difficulty levels (Easy, Medium, Hard)
- Real-time code execution and testing
- Progress tracking
- User authentication and profiles

## Tech Stack

- Backend: FastAPI (Python)
- Frontend: React
- Database: PostgreSQL
- ML Libraries: NumPy, Pandas, Scikit-learn

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the variables in `.env`
5. Initialize the database:
   ```bash
   alembic upgrade head
   ```
6. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Project Structure

```
ml_practice/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   └── schemas/
├── frontend/
├── tests/
└── alembic/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 