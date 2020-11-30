from enum import Enum

class NotificationType(Enum):
    IncreaseHP = "cfd5925d-95a8-45ab-8235-7114c798e36d"
    DecreaseHP = "54a3c5f7-c77e-4464-b4b3-ce4a729ca794"
    IncreaseXP = "5f85cc59-d959-4156-8fcc-df9ec205be23"
    DecreaseXP = "c5a30250-40ae-459d-9dff-d367b3d768a9"
    Die = "f17c9bdc-9b31-46aa-9a1b-60891ebd91c8"
    IncreaseLevel  = "0de713f1-476e-44ce-b137-44d794ba73b2"
    DecreaseLevel = "bd13b318-d507-4f4d-991d-87ccbcadaf04"

class GoalType(Enum):
    NotSet = "1a47112e-4a9b-43b1-90f4-cb253b66076f"
    Savings = "b174a548-a231-4f0c-aba7-a44cdd33a03d"
    Spending = "3cd3f1ab-0e7e-421e-bfac-31806d5dcde0"

class SpendingType(Enum):
    NotSet = "48fa1a83-aad4-4cea-ba98-d9a96b23eaee"
    TotalValue = "66f19410-345e-4b5a-95b8-a9dff3df1f68"
    NumberTransactions = "5670f1cb-7dfd-4573-866b-81aef195a9ac"

class BudgetCategory(Enum):
    Default = "321f37a9-40f8-4bd7-bb6f-ed1bca04f51f"
    Groceries = "e2cffbed-9d1b-4406-a17d-b22d23ea297d"
    Bills = "27f5d3ae-34ed-4359-8d28-21706983f82a"
    Transport = "35306148-55fe-4917-9ff9-c8f1aab672f0"
    Entertainment = "254b5b60-7483-4833-8132-c12d3705fb54"
    Other = "e58c8d58-b263-43f1-acd5-072e4d6ecb3a"
    Medical = "ef8bdc9f-5c10-471a-9362-3166ede16ea8"
    Education ="70926eae-ee48-46e8-8c27-ef7de2ac7ef2"
    Pets = "e072aa38-d345-46c1-9014-9bea1da77430"
    HobbiesSport = "00c93710-4708-465b-b885-0c9f474ad8b8"


    