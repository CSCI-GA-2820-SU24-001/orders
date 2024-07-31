Feature: The Orders service back-end
    As an orders service owner
    I need a RESTful catalog service
    So that I can keep track of all orders

Background:

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Order API" in the title
    And I should not see "404 Not Found"


    Scenario: Create an Order
        When I visit the "Home Page"
        And I press the "createOrder" button
        And I set the "Item IDs" to "1, 2, 3"
        # And I select "False" in the "Available" dropdown
        # And I select "Male" in the "Gender" dropdown
        And I set the "Item Quantities" to "1, 2, 3"
        And I set the "Shipping Address" to "New York, NY, USA"
        And I press the "SubmitOrder" button
        And I press the "closeOrderModal" button
        Then I should see "201" in the "Status" span
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