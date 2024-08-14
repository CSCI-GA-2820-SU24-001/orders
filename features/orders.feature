Feature: The Orders service back-end
    As an orders service owner
    I need a RESTful catalog service
    So that I can keep track of all orders

    Background:
        Given the following orders
            | id    | customer_id | shipping_address      | created_at                 | status     | items |
            | 00000 | 00111       | 725 Broadway NY 10003 | 2024-08-07 02:42:07.086311 | CREATED    | []    |
            | 00001 | 00222       | 726 Broadway NY 10003 | 2024-07-05 02:42:07.086311 | PROCESSING | []    |
            | 00002 | 00333       | 727 Broadway NY 10003 | 2024-08-02 02:42:07.086311 | COMPLETED  | []    |
            | 00003 | 00444       | 728 Broadway NY 10003 | 2024-08-01 02:42:07.086311 | CREATED    | []    |
        And the following items
            | id | order_id | product_id | price | product_description | quantity |
            | 0  | 0        | 0          | 23.4  | Glucose             | 2        |
            | 1  | 1        | 1          | 23.4  | Glucose             | 2        |
            | 2  | 2        | 2          | 23.4  | Glucose             | 2        |
            | 3  | 3        | 3          | 23.4  | Glucose             | 2        |

    Scenario: The server is running
        When I visit the "Home Page"
        Then I should see "Order API" in the title
        And I should not see "404 Not Found"


    Scenario: Create an Order
        When I visit the "Home Page"
        And I press the "createOrder" button
        And I set the "Item IDs" to "1"
        # And I select "False" in the "Available" dropdown
        # And I select "Male" in the "Gender" dropdown
        And I set the "Item Quantities" to "1"
        And I set the "Shipping Address" to "NY"
        And I press the "SubmitOrder" button
        And I press the "closeOrderModal" button
        Then I should see "201" in the "Status" span

    Scenario: View all Orders
        When I visit the "Home Page"
        And I press the "viewallorder" button
        Then I should see "725 Broadway NY 10003" in the results
        And I should see "726 Broadway NY 10003" in the results
        And I should see "727 Broadway NY 10003" in the results
        And I should see "728 Broadway NY 10003" in the results

    Scenario: Update an Order
        When I visit the "Home Page"
        And I press the "updateOrder" button
        And I set the "ID" to existing order id
        And I set the "Update Item IDs" to "1"
        # And I select "False" in the "Available" dropdown
        # And I select "Male" in the "Gender" dropdown
        And I set the "Update Item Quantities" to "1"
        And I set the "Update Shipping Address" to "UPDATE"
        And I press the "UpdateCurrOrder" button
        And I press the "updatecloseordermodal" button
        Then I should see "200" in the "Status" span

    Scenario: View all Items
        When I visit the "Home Page"
        And I press the "viewallitems" button
        Then I should see "Glucose" in the item results
        And I should see "Candy" in the item results
    Scenario: Read an Order
        When I visit the "Home Page"
        And I set the "Order ID" to "00000"
        And I press the "readOrder" button
        Then I should see "725 Broadway NY 10003" in the "Shipping Address" field
        And I should see "00000" in the "Customer ID" field
        And I should see "CREATED" in the "Status" field
        And I should see "Product ID: 0, Description: Glucose, Quantity: 2, Price: 23.4" in the "Items" field

    # When I copy the "Id" field
    # And I press the "Clear" button
    # Then the "Id" field should be empty
    # And the "Name" field should be empty
    # And the "Category" field should be empty
    # When I paste the "Id" field
    # And I press the "Retrieve" button
    # Then I should see the message "Success"
    # And I should see "Happy" in the "Name" field
    # And I should see "Hippo" in the "Category" field
    # And I should see "False" in the "Available" dropdown
    # And I should see "Male" in the "Gender" dropdown
    # And I should see "2022-06-16" in the "Birthday" field


    Scenario: Query Completed Orders
        When I visit the "Home Page"
        And I select "Completed" in the "Order Status" dropdown
        Then I should see the message "Success"
        And I should see "727 Broadway NY 10003" in the results
        And I should see "COMPLETED" in the results
        And I should not see "CREATED" in the results


    Scenario: Query Orders by Customer ID
        When I visit the "Home Page"
        And I press the "searchbycustomerid" button
        And I set the "Customer ID" to "111"
        And I press the "searchcustomerid" button
        Then I should see the message "Success"
        And I should see "111" in the results
        And I should not see "222" in the results
        And I should not see "333" in the results
        And I should not see "444" in the results

    Scenario: Action - Change order status
        When I visit the "Home Page"
        And I select "Processing" in the "Order Status" dropdown
        Then I should see the message "Success"
        And I should see "PROCESSING" in the results
        When I copy the "Order ID" field
        And I press the "changeorderstatus" button
        And I paste the "ID update" field
        And I select "Completed" in the "New Order Status" dropdown
        And I press the "updatestatus" button
        Then I should see the message "Success"

    Scenario: Delete an Order
        When I visit the "Home Page"
        And I press the "deleteOrder" button
        And I set the "order ID" to existing order id
        And I press the "DeleteCurrOrder" button
        And I press the "closedeleteOrderModal" button
        Then I should see "Deleted Successfully (204)" in the "Status" span