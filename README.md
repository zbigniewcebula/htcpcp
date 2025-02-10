# HTCPCP Server

This project implements an HTCPCP (Hyper Text Coffee Pot Control Protocol) server that can handle various requests related to brewing coffee and tea. The server is built on top of HTTP, so it handles it's methods, including `BREW`, `GET`, `POST`, `PROPFIND`. `OPTIONS`, and `WHEN`.

## Story
One day, while I was engaged in my usual activities (memes and games), my fiancé asked me about error that appeared on some website. It happened that my fiancé became a student of university in our home city (Łódź, Poland) and their website that handles stuff related to student grades and so on is called USOS.
USOS is famous of being a trash webapp, this time IT dept decided to leave it in "Forbiddedn 403" state. 
My beloved wanted to understand if she did something wrong or they just screw up. 
I was in my autistic mood, so I started explaining to her all the HTTP codes. 
I always knew the joke about 418 error code so also this was a subject of my autistic explosion. 
Five minutes later when she went back to hers stuff, I decided to search a bit about teapot stuff. 
Then I found the [HTCPCP RFC](https://datatracker.ietf.org/doc/html/rfc2324).
Obviously I started to be curious if somebody decided to implement that, howerer I was lazy, so I found only the implementation of something related to Raspberry Pi hobby project.
> Idea.exe

I decided to implement something on a base of HTCPCP idea, but a bit extended by my imagination.
The main goal is: server that serves virtual coffee or tea.
Obviously I have no idea expertise idea in any of those fields, so the bawsic implementation may be a crap ¯\\_(ツ)_/¯

## Features

- Brew coffee or tea with optional additions.
- Check the status of brewers and beverages.
- Handle milk additions and pouring.
- Fetch images of brewed beverages using OpenAI API. (optional)
- Gather completed beverages.
- Return responses in JSON or XML format.
- Time synchronization using NTP.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/htcpcp-server.git
    cd htcpcp-server
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. (Optional) Add your OpenAI API key to `SECRET.py`:
    ```python
    OPENAI_KEY = "your-openai-api-key-here"
    ```

## Usage

1. Start the HTCPCP server:
    ```sh
    python htcpcp.py
    ```

2. Use `curl` or any HTTP client to interact with the server. Here are some example commands:

    - Brew coffee:
        ```sh
        curl -X POST -H "Content-Type: application/coffee-pot-command" http://localhost:8080
        ```

    - Brew tea with milk additions:
        ```sh
        curl -X POST -H "Content-Type: application/tea-pot-command" -H "Accept-Additions: Milk:2" http://localhost:8080
        ```

    - Check the status of brewers:
        ```sh
        curl http://localhost:8080/brewer
        ```

    - Fetch a brewed beverage:
        ```sh
        curl http://localhost:8080/check
        ```

    - Gather a completed beverage:
        ```sh
        curl -X GET http://localhost:8080/gather
        ```

    - Get the status in XML format:
        ```sh
        curl -X PROPFIND http://localhost:8080/brewer
        ```

## Console Parameters

- `--port` or `-p`: Port to run the server on (default: 8080)
- `--host` or `-ip`: Host to run the server on (default: localhost)
- `--coffee-only` or `-co`: Enable coffee only mode
- `--tea-only` or `-to`: Enable tea only mode

## Contributing

Contributions are welcome! 
Feel free to critic and correct my trash-level code quality.
Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.
