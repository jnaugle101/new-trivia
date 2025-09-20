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
    {"q": "Which Kitchen Nightmares celebrity chef is also one of the judges on MasterChef?", "a": "Gordon Ramsay", "category": "Pop Culture"},
    {"q": "What candy brand encourages people to taste the rainbow?”, "a": "Skittles", "category": "Pop Culture"},
    {"q": "Restaurants serving up bibimbap, tteokbokki, and japchae have spread all over the world, but where do these dishes originate?", "a": "Korea", "category": "Pop Culture"},
    {"q": "Who is the author of the cookbook Salt, Fat, Acid, Heat?", "a": "Samin Nosrat", "category": "Pop Culture"},
    {"q": "What cooking method involves submerging food in a water bath at a precise temperature?", "a": "Sous vide", "category": "Pop Culture"},
    {"q": "Who is known as the Barefoot Contessa?", "a": "Ina Garten", "category": "Pop Culture"},
    {"q": "What type of cuisine is the focus of the show The Great British Bake Off?", "a": "British baking","category": "Pop Culture"},
    {"q": "Which chef is known for the catchphrase Bam!?”, "a": "Emeril Lagasse", "category": "Pop Culture"},
    {"q": " Who is the celebrity chef known for the cooking show 30-Minute Meals?", "a": "Rachael Ray", "category": "Pop Culture"},
    # optional image question
    #{"q": "Name this artist", "a": "Beyoncé", "category": "Pop Culture", "image": "https://.../beyonce.jpg"},

]

# Optional: you can compute the category list from the data.
CATEGORIES = sorted({q["category"] for q in QUESTIONS})
