import mysql.connector

# Establish MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mca123",
    database="mycart"
)
cursor = db.cursor()


class Product:
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price


class Category:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.products = []

    def add_product(self, product):
        self.products.append(product)


class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, product, quantity):
        self.items.append({"product": product, "quantity": quantity})

    def remove_item(self, index):
        del self.items[index]

    def calculate_total(self):
        total = 0
        for item in self.items:
            total += item["product"].price * item["quantity"]
        return total

    def generate_bill(self, discount):
        total = self.calculate_total()
        discounted_amount = total - discount
        final_amount = discounted_amount if discounted_amount > 0 else total
        print("Bill Details:")
        print("Total amount: Rs", total)
        print("Discounted amount: Rs", discounted_amount)
        print("Final amount: Rs", final_amount)

        # Store the bill in the database
        query = "INSERT INTO bills (total_amount, discounted_amount, final_amount) VALUES (%s, %s, %s)"
        values = (total, discounted_amount, final_amount)
        cursor.execute(query, values)
        db.commit()


class MyCartApp:
    def __init__(self):
        self.categories = []
        self.cart = Cart()

    def add_category(self, category):
        self.categories.append(category)

    def find_category(self, category_id):
        for category in self.categories:
            if category.id == category_id:
                return category
        return None

    def display_categories(self):
        print("Categories:")
        for category in self.categories:
            print(category.id, "-", category.name)

    def display_products(self, category_id):
        category = self.find_category(category_id)
        if category:
            print("Products in", category.name, "category:")
            for product in category.products:
                print(product.id, "-", product.name, "(Rs", product.price, ")")
        else:
            print("Category not found.")

    def display_product_details(self, product_id):
        for category in self.categories:
            for product in category.products:
                if product.id == product_id:
                    print("Product details:")
                    print("ID:", product.id)
                    print("Name:", product.name)
                    print("Price: Rs", product.price)
                    return
        print("Product not found.")

    def add_product_to_cart(self, product_id, quantity):
        for category in self.categories:
            for product in category.products:
                if product.id == product_id:
                    self.cart.add_item(product, quantity)
                    print("Product added to cart.")
                    return
        print("Product not found.")

    def remove_product_from_cart(self, index):
        try:
            self.cart.remove_item(index)
            print("Product removed from cart.")
        except IndexError:
            print("Invalid item index.")

    def buy_products(self):
        discount = 500 if self.cart.calculate_total() > 10000 else 0
        self.cart.generate_bill(discount)

# Sample usage
app = MyCartApp()

query = "SELECT * FROM categories"
cursor.execute(query)
categories_data = cursor.fetchall()

for category_data in categories_data:
    category_id, category_name = category_data
    category = Category(category_id, category_name)

    query = "SELECT * FROM products WHERE category_id = %s"
    values = (category_id,)
    cursor.execute(query, values)
    products_data = cursor.fetchall()

    for product_data in products_data:
        product_id, product_name, product_price, _ = product_data
        product = Product(product_id, product_name, product_price)
        category.add_product(product)

    app.add_category(category)

# Display categories and products
app.display_categories()
category_id = int(input("Enter the category ID to view products: "))
app.display_products(category_id)

# Display product details
product_id = int(input("Enter the product ID to view details: "))
app.display_product_details(product_id)

# Add products to cart
add_more = True
while add_more:
    product_id = int(input("Enter the product ID to add to cart (or 0 to finish): "))
    if product_id == 0:
        add_more = False
    else:
        quantity = int(input("Enter the quantity: "))
        app.add_product_to_cart(product_id, quantity)

# Display cart
print("Cart items:")
for i, item in enumerate(app.cart.items):
    print(i, "-", item["product"].name, "(Quantity:", item["quantity"], ")")

# Remove product from cart
index = int(input("Enter the index of the item to remove: "))
app.remove_product_from_cart(index)

# Buy products and generate bill
app.buy_products()

# Close MySQL connection
cursor.close()
db.close()
