# use file to get the data from database, could be simple google sheets or 


def get_board_token() -> list[str]:
    with open("./public/board_tokens.txt", "r") as file:
        return file.read().splitlines()
