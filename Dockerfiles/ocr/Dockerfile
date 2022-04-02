FROM buildpack-deps:bullseye
MAINTAINER Koray YILMAZ <kyilmaz80@gmail.com>

ENV LEPTONICA_VER 1.82.0

# build essentials
RUN apt-get update && apt-get install -y --install-recommends \
	wget \
    git \
	autoconf-archive \
    make \
    automake \
	g++ \
	libtool \
	libleptonica-dev \
	pkg-config \
	libpango1.0-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# leptonica build
WORKDIR /usr/local/src/
RUN wget http://www.leptonica.org/source/leptonica-${LEPTONICA_VER}.tar.gz && \
	tar xvzf leptonica-${LEPTONICA_VER}.tar.gz && \
	cd leptonica-${LEPTONICA_VER} && \
    ./configure && \
    make && \
    make install && \
    rm -f /usr/local/src/leptonica-${LEPTONICA_VER}.tar.gz && \
	rm -rf /usr/local/src/leptonica-${LEPTONICA_VER}

# tesseract build
RUN rm -rf tesseract-ocr
RUN git clone --depth 1  https://github.com/tesseract-ocr/tesseract.git tesseract-ocr && \
	wget https://github.com/tesseract-ocr/tessdata/raw/main/tur.traineddata && \
	wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata && \
  	cd tesseract-ocr && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install && \
    make install-langs && \
    ldconfig && \
    cd .. && \
    cp *.traineddata  /usr/local/share/tessdata/
 
# python ocr tutorial
WORKDIR /opt
RUN rm -rf python_ocr_tutorial/
RUN	git clone https://github.com/kyilmaz80/python_ocr_tutorial/ && \
	cd /opt/python_ocr_tutorial/ && \
	pip install --upgrade pip && \
	pip install -r requirements.txt

WORKDIR /opt/python_ocr_tutorial/flask_server

EXPOSE 80
CMD ["python3", "app.py"]

