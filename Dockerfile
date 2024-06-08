#Base Image
FROM python:3.10

ENV PYTHONUNBUFFERED=1

#Install Package
RUN apt update && apt install -y \
    build-essential \
    binutils \
    libproj-dev \
    python3-gdal \
    python3-gdl \
    gdal-bin \
    net-tools 

# Create Folder
#RUN mkdir -p /api

#Set Workdir & Copy App
WORKDIR /app
COPY . .

#Install Python Package with requirements file
RUN pip install --no-cache-dir -r requirements.txt

#Expose Port
EXPOSE 8000

#
RUN mkdir -p static/upload
RUN echo yes | python3 manage.py collectstatic
CMD ["python3","manage.py","runserver","0.0.0.0:8000"]

