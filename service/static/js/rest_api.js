$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#order_id").val(res.id);
        $("#order_name").val(res.name);
        $("#order_category").val(res.category);
        if (res.available == true) {
            $("#order_available").val("true");
        } else {
            $("#order_available").val("false");
        }
        $("#order_gender").val(res.gender);
        $("#order_birthday").val(res.birthday);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#order_name").val("");
        $("#order_category").val("");
        $("#order_available").val("");
        $("#order_gender").val("");
        $("#order_birthday").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#orders_status").empty();
        $("#orders_status").append(message);
    }
       // ****************************************
    // Read an order and show in modal
    // ****************************************
 // Get the modal
var modal = document.getElementById("readOrderModal");

// Get the button that opens the modal
var btn = document.getElementById("readOrderBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal
btn.onclick = function() {
  modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

// Fetch Order when "Fetch Order" button is clicked in the modal
document.getElementById("fetchOrderBtn").onclick = function() {
  var orderId = document.getElementById("orderIdInput").value;

  if (!orderId) {
    alert("Please enter an Order ID.");
    return;
  }

  // Fetch the order details
  // Note: You need to replace this with your actual API call
  fetch(`/orders/${orderId}`)
    .then(response => response.json())
    .then(data => {
      updateTable(data);
      modal.style.display = "none"; // Close the modal after fetching
    })
    .catch(error => {
      console.error("Error fetching order:", error);
      alert("No order found.");
    });
};

// Function to update the existing table with the order details
function updateTable(order) {
  var table = document.getElementById("search-results-body");
  
  // Clear previous data if you want to replace the existing content
  table.innerHTML = ""; 

  // Add new row with fetched order details
  var row = document.createElement("tr");

  row.innerHTML = `
    <td>${order.id}</td>
    <td>${order.customer_id}</td>
    <td>${order.created_at}</td>
    <td>${order.shipping_address}</td>
    <td>${order.status}</td>
    <td>${order.items.map(item => item.id).join(", ")}</td>
  `;

  table.appendChild(row);
}

    // ****************************************
    // Create a order
    // ****************************************

    $("#create-btn").click(function () {

        let name = $("#order_name").val();
        let category = $("#order_category").val();
        let available = $("#order_available").val() == "true";
        let gender = $("#order_gender").val();
        let birthday = $("#order_birthday").val();

        let data = {
            "name": name,
            "category": category,
            "available": available,
            "gender": gender,
            "birthday": birthday
        };

        $("#orders_status").empty();

        let ajax = $.ajax({
            type: "POST",
            url: "/orders",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a order
    // ****************************************

    $("#update-btn").click(function () {

        let order_id = $("#order_id").val();
        let name = $("#order_name").val();
        let category = $("#order_category").val();
        let available = $("#order_available").val() == "true";
        let gender = $("#order_gender").val();
        let birthday = $("#order_birthday").val();

        let data = {
            "name": name,
            "category": category,
            "available": available,
            "gender": gender,
            "birthday": birthday
        };

        $("#orders_status").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a order
    // ****************************************

    $("#retrieve-btn").click(function () {

        let order_id = $("#order_id").val();

        $("#orders_status").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a order
    // ****************************************

    $("#delete-btn").click(function () {

        let order_id = $("#order_id").val();

        $("#orders_status").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            clear_form_data()
            flash_message("order has been Deleted!")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#order_id").val("");
        $("#orders_status").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a order
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#order_name").val();
        let category = $("#order_category").val();
        let available = $("#order_available").val() == "true";

        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (category) {
            if (queryString.length > 0) {
                queryString += '&category=' + category
            } else {
                queryString += 'category=' + category
            }
        }
        if (available) {
            if (queryString.length > 0) {
                queryString += '&available=' + available
            } else {
                queryString += 'available=' + available
            }
        }

        $("#orders_status").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/orders?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Category</th>'
            table += '<th class="col-md-2">Available</th>'
            table += '<th class="col-md-2">Gender</th>'
            table += '<th class="col-md-2">Birthday</th>'
            table += '</tr></thead><tbody>'
            let firstorder = "";
            for (let i = 0; i < res.length; i++) {
                let order = res[i];
                table += `<tr id="row_${i}"><td>${order.id}</td><td>${order.name}</td><td>${order.category}</td><td>${order.available}</td><td>${order.gender}</td><td>${order.birthday}</td></tr>`;
                if (i == 0) {
                    firstorder = order;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstorder != "") {
                update_form_data(firstorder)
            }

            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

})


$(document).ready(function () {
    const url = "/orders"

    // Function to fetch JSON data
    function fetchJSONData() {
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            success: function (response) {
                // Process the JSON response
                fillTable(response);
            },
            error: function (error) {
                console.log('Error fetching data', error);
            }
        });
    }

    // Function to fill the existing table with JSON data
    function fillTable(data) {
        if (data.length === 0) {
            $('#search_results').html('<p>No data available</p>');
            return;
        }

        // Get table body element
        const tbody = $('#search-results-body');

        // Clear any existing content
        tbody.empty();

        // Create table rows
        data.forEach(item => {
            const row = $('<tr>');
            // Only add the first and second properties
            const values = Object.values(item);
            // Assuming the structure is known, you can directly access the values you want to keep
            const created_at = values[0];
            const customer_id = values[1];
            const order_id = values[2];
            const items = values[3];
            const shipping_address = values[4];
            const status = values[5];

            $.ajax({
                url: "/orders/" + order_id + "/items",
                type: 'GET',
                dataType: 'json',
                success: function (response) {
                    // Process the JSON response
                    // var st = '';
                    // for (resp in response) {
                    //     st = st + resp["id"] + ",";
                    // }
                    const ids = response.map(item => item.id);
                    row.append($('<td>').text(ids));
                    console.log("RESPONSE");
                    console.log(response);
                },
                error: function (error) {
                    console.log('Error fetching data', error);
                }
            });

            // Append only the desired columns
            row.append($('<td>').text(order_id));
            row.append($('<td>').text(customer_id));
            row.append($('<td>').text(created_at));
            // row.append($('<td>').text(items));
            console.log("ITEMS: ");
            console.log(items);
            row.append($('<td>').text(shipping_address));
            row.append($('<td>').text(status));


            tbody.append(row);
        });

    }

    // Attach click event listener to the button
    $('#viewallorder-btn').click(function () {
        fetchJSONData();
    });
});


// FUNCTION TO FILL ITEM TABLE
$(document).ready(function () {
    const url = "/orders"

    // Function to fetch JSON data
    function fetchJSONDataItems() {
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            success: function (response) {
                // Process the JSON response
                fillTableItems(response);
            },
            error: function (error) {
                console.log('Error fetching data', error);
            }
        });
    }

    // Function to fill the existing table with JSON data
    function fillTableItems(data) {
        if (data.length === 0) {
            $('#search_results_items').html('<p>No data available</p>');
            return;
        }

        // Get table body element
        const tbody = $('#search-results-body-items');

        // Clear any existing content
        tbody.empty();
        var done_prods = []

        // Create table rows
        data.forEach(item => {
            const row = $('<tr>');
            const values = Object.values(item);
            const order_id = values[2];

            $.ajax({
                url: "/orders/" + order_id + "/items",
                type: 'GET',
                dataType: 'json',
                success: function (response) {
                    console.log(response);
                    response.forEach(item => {
                        let row = $('<tr></tr>');
                        var item_id = item["id"];
                        var product_id = item["product_id"];


                        var order_id = item["order_id"];
                        var price = item["price"];
                        var product_desc = item["product_description"];
                        var quantity = item["quantity"];
                        if (done_prods.indexOf(product_id) == -1) {
                            // row.append($('<td></td>').text(item_id));
                            row.append($('<td></td>').text(product_id));
                            row.append($('<td></td>').text(price));
                            row.append($('<td></td>').text(product_desc));

                            done_prods.push(product_id);
                            console.log("ARRAY");
                            console.log(done_prods);
                            tbody.append(row);
                        }
                    });
                },
                error: function (error) {
                    console.log('Error fetching data', error);
                }
            });

            tbody.append(row);
        });

    }

    // Attach click event listener to the button
    $('#viewallitems-btn').click(function () {
        fetchJSONDataItems();
    });
});

var modal = document.getElementById("orderModal");

var btn = document.getElementById("createorder-btn");

var span = document.getElementsByClassName("close")[0];

btn.onclick = function () {
    modal.style.display = "block";
}

span.onclick = function () {
    modal.style.display = "none";
}

window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

document.getElementById("orderForm").onsubmit = function (event) {
    event.preventDefault();
    var isValid = true;

    // Validate Order Name
    // var orderName = document.getElementById("orderName").value;
    // if (!orderName) {
    //     document.getElementById("orderNameError").style.display = "block";
    //     isValid = false;
    // } else {
    //     document.getElementById("orderNameError").style.display = "none";
    // }

    // Validate Item IDs
    var itemIds = document.getElementById("orders_item_ids").value;
    if (!itemIds) {
        document.getElementById("itemIdsError").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("itemIdsError").style.display = "none";
    }

    // Validate Item Quantities
    var itemQuantities = document.getElementById("orders_item_quantities").value;
    if (!itemQuantities) {
        document.getElementById("itemQuantitiesError").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("itemQuantitiesError").style.display = "none";
    }

    // Validate Shipping Address
    var shippingAddress = document.getElementById("orders_shipping_address").value;
    if (!shippingAddress) {
        document.getElementById("shippingAddressError").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("shippingAddressError").style.display = "none";
    }

    // If all fields are valid, create JSON object
    if (isValid) {
        // var orderData = {
        //     itemIds: itemIds,
        //     itemQuantities: itemQuantities,
        //     shippingAddress: shippingAddress
        // };

        // var orderJSON = JSON.stringify(orderData);
        // console.log(orderJSON);

        const array_ids = itemIds.split(',');
        const array_quantities = itemQuantities.split(',');

        var array_ids_temp = new Array();
        var array_item_temp = new Array();

        console.log("ARRAY ITEM STRING: ");
        console.log("ARRAY IDS STRING: ");

        console.log(array_ids);
        console.log(array_quantities);


        for (var i = 0; i < array_ids.length; i++) {
            array_ids_temp[i] = parseInt(array_ids[i].replace(/\s/g, ''), 10);
            if (isNaN(array_ids_temp[i])) {
                alert("Invalid Input");
                return
            }
        }

        for (var i = 0; i < array_quantities.length; i++) {
            array_item_temp[i] = parseInt(array_quantities[i].replace(/\s/g, ''), 10);
            if (isNaN(array_item_temp[i])) {
                alert("Invalid Input");
                return
            }
        }
        console.log("ARRAY ITEM: ");
        console.log("ARRAY IDS: ");

        console.log(array_item_temp);
        console.log(array_ids_temp);

        if (array_ids.length != array_quantities.length) {
            alert("Number of item IDs and quantities must match");
            return;
        }


        var requestObject = createRequestObject(array_ids_temp, array_item_temp, shippingAddress);
        console.log(JSON.stringify(requestObject));

        let ajax = $.ajax({
            type: "POST",
            url: "/orders",
            contentType: "application/json",
            data: JSON.stringify(requestObject),
        });

        ajax.done(function (res, textStatus, xhr) {
            flash_message_create(res)
            console.log("RESULT: ");
            console.log(res);
            console.log(xhr.status);
            $("#orders_status").text(xhr.status);
        });

        ajax.fail(function (res) {
            flash_message_create(res.responseJSON.message)
            console.log(res);
        });
    }
}
function generateRandomCustomerId() {
    return Math.floor(Math.random() * 10001);
}

function getCurrentDate() {
    var date = new Date();
    return date.toUTCString();
}

function flash_message_create(message) {
    $("#orders_status").empty();
    $("#orders_status").append(message);
}

function createRequestObject(itemIds, itemQuantities, shippingAddress) {
    var items = itemIds.map((itemId, index) => ({
        product_id: parseInt(itemId),
        order_id: 0,
        quantity: parseInt(itemQuantities[index]),
        price: 23.4,
        product_description: "Glucose"
    }));

    var request = {
        items: items,
        customer_id: generateRandomCustomerId(),
        shipping_address: shippingAddress,
        created_at: getCurrentDate(),
        status: "CREATED"
    };

    return request;
}


