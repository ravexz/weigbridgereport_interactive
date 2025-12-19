# Greenfield Weighbridge Report System

Interactive report generation system with advanced analytics for tea leaf collection tracking.

## Features

- 📊 **Advanced Analytics Dashboard** - 10+ interactive charts including time-series trends, heatmaps, and predictive forecasting
- 📄 **Dual Report Format** - Generate both PDF (Excel-based) and interactive HTML reports
- 🗄️ **PostgreSQL Database** - Normalized schema with lookup tables for data integrity
- 📧 **Email Delivery** - Automated report distribution
- 🔍 **Interactive Filtering** - Client-side filtering and sorting in HTML reports
- 📱 **Responsive Design** - Modern UI with Tailwind CSS and glassmorphism

## Tech Stack

**Backend:**
- FastAPI (Python)
- PostgreSQL with psycopg2
- win32com for Excel/PDF generation
- openpyxl for Excel manipulation

**Frontend:**
- React + TypeScript
- Vite
- Recharts for data visualization
- Tailwind CSS

## Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Microsoft Excel (for PDF generation)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ravexz/weigbridgereport_interactive.git
   cd weigbridgereport_interactive
   ```

2. **Backend setup:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database setup:**
   - Create PostgreSQL database:
     ```sql
     CREATE DATABASE greenfield_reports;
     ```
   - Copy `.env.example` to `.env` and configure your database credentials
   - Initialize database:
     ```bash
     python backend/database.py
     ```

4. **Frontend setup:**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start backend:**
   ```bash
   uvicorn backend.main:app --reload
   ```

2. **Start frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Environment Variables

Create a `.env` file in the root directory (see `.env.example`):

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=greenfield_reports
DB_USER=postgres
DB_PASSWORD=your_password

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_RECIPIENT=recipient@example.com
```

## Database Schema

The system uses a normalized PostgreSQL schema:

- `zones` - Collection zones
- `routes` - Routes within zones
- `vehicles` - Vehicle registry
- `clerks` - Clerk registry
- `daily_entries` - Main collection records with foreign keys

## Advanced Analytics

The Analysis tab includes:

1. **Time-Series Quality Trends** - Dual Y-axis showing quality % and weight over time
2. **Clerk Performance** - Top 10 clerks ranked by collection volume
3. **Vehicle Utilization** - Fleet usage tracking
4. **Heatmap Calendar** - 90-day collection pattern visualization
5. **Comparative Analysis** - Multi-zone performance comparison
6. **Predictive Trends** - 7-day moving average with forecast

## License

MIT

## Author

Greenfield Tea Collection System
