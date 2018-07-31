FROM buildpack-deps:stretch
MAINTAINER Koray YILMAZ <kyilmaz80@gmail.com>

ENV LEPTONICA_VER 1.74.4
ENV TESSERACT_STABLE_VER 3.04.01

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
    python-pip \
    supervisor \
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
RUN rm -rf /usr/local/lib/libtess*
RUN git clone https://github.com/tesseract-ocr/tesseract.git --branch ${TESSERACT_STABLE_VER} --single-branch tesseract-ocr && \
	wget https://github.com/tesseract-ocr/tessdata/raw/3.04.00/tur.traineddata && \
	wget https://github.com/tesseract-ocr/tessdata/raw/3.04.00/eng.traineddata && \
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
RUN	git clone https://github.com/kyilmaz80/python_ocr_tutorial/
RUN	pip install --upgrade pip 
RUN cd /opt/python_ocr_tutorial && pip install -r requirements.txt

WORKDIR /opt/python_ocr_tutorial/flask_server

COPY run.sh /
COPY etc/supervisord.conf /etc/supervisord.conf
COPY etc/supervisord.d/*.ini /etc/supervisord.d/
RUN chmod +x /run.sh

EXPOSE 80
CMD ["/run.sh"]

