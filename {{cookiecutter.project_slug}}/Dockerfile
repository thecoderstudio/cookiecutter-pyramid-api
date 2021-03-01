FROM python:3.9

RUN addgroup {{cookiecutter.project_slug}}
RUN useradd -g {{cookiecutter.project_slug}} {{cookiecutter.project_slug}}

COPY . /home/{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}
WORKDIR /home/{{cookiecutter.project_slug}}

RUN pip install -e {{cookiecutter.project_slug}}[tests]
RUN pip install pytest-cov~=2.11

# Download wait-for-it to allow waiting for dependency containers
RUN mkdir util
RUN curl https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh > util/wait-for-it.sh
RUN chmod +x util/wait-for-it.sh

WORKDIR /home/{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}

EXPOSE {{cookiecutter.api_port}}
ENTRYPOINT ["pserve"]
CMD ["settings.ini", "--reload"]
