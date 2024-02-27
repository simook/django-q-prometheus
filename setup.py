from setuptools import setup

setup(
    name='django-q-prometheus',
    packages=['django_q_prometheus'],
    description='django-q performance metrics',
    version='1.0.0',
    url='http://github.com/simook/django-q-prometheus',
    author='Kyle Simukka',
    author_email='kylesimukka@gmail.com',
    keywords=['django-q','prometheus','metrics'],
    install_requires=[
        'django',
        'django-q',
        'prometheus-client',
    ],
)