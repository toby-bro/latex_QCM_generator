# Use official Python runtime as base image
FROM ghcr.io/astral-sh/uv:debian

# Install LaTeX and required packages
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-lang-french \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY qcm_generator/ ./qcm_generator/

# Install only production dependencies
RUN uv sync --no-dev

# Create necessary directories
RUN mkdir -p /app/qcm_generator/subjects

# Expose Flask port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=qcm_generator.main_flask
ENV PYTHONUNBUFFERED=1

# Run the Flask application
CMD ["uv", "run", "--no-sync", "-m", "qcm_generator.main_flask"]
