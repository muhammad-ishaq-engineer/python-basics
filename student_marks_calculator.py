name = input("Enter your name: ")


english = int(input("Enter English marks: "))
dld = int(input("Enter your DLD marks: "))
islamiyat = int(input("Enter your Islamiat marks: "))
pak_studies = int(input("Enter your Pakistan Studies marks: "))
itcp = int(input("Enter your ITCP marks: "))
apply_phy = int(input("Enter your Applied Physics marks: "))
ohse = int(input("Enter your OHSE marks: "))
math = int(input("Enter your Math marks: "))

total = english + dld + islamiyat + pak_studies + itcp + apply_phy + ohse + math

percentage = (total / 800) * 100

print("\n---- STUDENT RESULT ----")
print("Name:", name)
print("Total:", total)
print("Percentage:", percentage)

if percentage >= 80:
    print("Grade: A+")
    print("Result: Pass")
elif percentage >= 70:
    print("Grade: A")
    print("Result: Pass")
elif percentage >= 60:
    print("Grade: B")
    print("Result: Pass")
elif percentage >= 50: 
    print("Grade: C")
    print("Result: Pass")
elif percentage >= 40:
    print("Grade: D")
    print("Result: Pass")
else:
    print("Grade: F")
    print("Result: Fail")
