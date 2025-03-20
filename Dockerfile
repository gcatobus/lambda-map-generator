# Set the base image
FROM public.ecr.aws/lambda/python:latest
LABEL description="Generate a map of the US with Alaska, Hawaii, and Puerto Rico layered in"
LABEL version="1.0"

# Set Matplotlib's config directory to a writable location
ENV MPLCONFIGDIR=/tmp

# Set the working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy application files
COPY . ${LAMBDA_TASK_ROOT}

# Set permissions
RUN chmod -R 755 ${LAMBDA_TASK_ROOT}/shape/
RUN chmod -R 755 ${LAMBDA_TASK_ROOT}/image/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Command to run the application
CMD ["main.handler"]