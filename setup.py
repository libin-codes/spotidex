from setuptools import setup,find_packages
setup(
    name="spotidex",
    version="0.0.1",
    description="Download spotify songs , playlist and albums for free",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "mutagen==1.47.0",
        "Requests==2.31.0",
        "rich==13.7.1",
        "spotipy==2.23.0",
        "textual==0.55.1",
        "tqdm==4.66.1",
        "yt_dlp==2024.3.10",
        "ytmusicapi==1.3.2",
    ],
    author="libin-codes",
    author_email="libinlalu000@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "spotidex = spotidex:main",  
        ],
    },
    python_requires=">=3.10",
)

