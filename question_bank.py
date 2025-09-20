# question_bank.py

QUESTIONS = [
    # --- Geography ---
    {"q": "What is the capital of France?", "a": "Paris", "category": "Geography"},
    {"q": "Mount Everest is on the border of which two countries?", "a": "Nepal and China", "category": "Geography"},
    {"q": "Which U.S. state is nicknamed the Sunshine State?", "a": "Florida", "category": "Geography"},
    {"q": "What country is also called Holland?", "a": "Netherlands", "category": "Geography"},
    {"q": "Which two countries share the longest international border?", "a": "United States and Canada",
     "category": "Geography"},

    # --- History ---
    {"q": "In what year did the United States declare independence?", "a": "1776", "category": "History"},
    {"q": "Who was the first President of the United States?", "a": "George Washington", "category": "History"},
    {"q": "Who wrote the Declaration of Independence?", "a": "Thomas Jefferson", "category": "History"},
    {"q": "What year did World War II end?", "a": "1945", "category": "History"},

    # --- Science ---
    {"q": "What is H2O commonly known as?", "a": "Water", "category": "Science"},
    {"q": "How many bones are in the adult human body?", "a": "206", "category": "Science"},
    {"q": "What gas do plants absorb from the atmosphere?", "a": "Carbon dioxide", "category": "Science"},

    # --- Movies & TV ---
    {"q": "What 1997 film stars Will Smith and Tommy Lee Jones as agents who police aliens?", "a": "Men in Black", "category": "Movies & TV"},
    {"q": "What’s the name of the wizarding school in Harry Potter?", "a": "Hogwarts", "category": "Movies & TV"},

    # --- Sports ---
    {"q": "How many players are on the field for one soccer team?", "a": "11", "category": "Sports"},
    {"q": "How many holes are played in a standard round of golf?", "a": "18", "category": "Sports"},

    # --- General ---
    {"q": "What is the largest organ of the human body by weight?", "a": "Skin", "category": "General"},
    {"q": "What does URL stand for?", "a": "Uniform Resource Locator", "category": "General"},

    # Pop Culture
    {"q": "What is Taylor Swift’s fanbase called?", "a": "Swifties", "category": "Pop Culture"},
    {"q": "Who plays Iron Man in the MCU?", "a": "Robert Downey Jr.", "category": "Pop Culture"},
    {"q": "What Netflix show features the Upside Down?", "a": "Stranger Things", "category": "Pop Culture"},
    {"q": "Finish the brand: Ben & ____", "a": "Jerry's", "category": "Pop Culture"},
    {"q": "What 2016 mobile game had players catching creatures in AR?", "a": "Pokémon Go", "category": "Pop Culture"},
    # optional image question
    #{"q": "Name this artist", "a": "Beyoncé", "category": "Pop Culture", "image": "https://.../beyonce.jpg"},

]

# Optional: you can compute the category list from the data.
CATEGORIES = sorted({q["category"] for q in QUESTIONS})
