Feature: The pet store service back-end
    As a web store owner
    I need a RESTful catalog service
    So that I can keep track of all orders

    @wip
    Scenario: The server is running
        When I visit the "Home Page"
        Then I should see "Order RESTful Service" in the title
        And I should not see "404 Not Found"