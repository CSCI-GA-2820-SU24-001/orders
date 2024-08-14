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
// Read an order 
// ****************************************

// Get the modal
var modal = document.getElementById("readOrderModal");

// Get the button that opens the modal
var btn = document.getElementById("readorder-btn");

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
$("#fetchorder-btn").click(function (event) {
    event.preventDefault();

    let orderId = $("#orders_readorder_id").val();

    if (!orderId) {
        
        return;
    }

    $("#orders_status").empty();

    let ajax = $.ajax({
        type: "GET",
        url: `/orders/${orderId}`,
        contentType: "application/json",
    });

    ajax.done(function (res) {
        console.log(res);
        updateTable(res);  // Function to update the table with the order details
        modal.style.display = "none"; // Close the modal after fetching
        flash_message("200");
    });

    ajax.fail(function (res) {
        console.error("Error fetching order:", res);
        flash_message("No order found or error occurred.");
    });
    return false;
});

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
            const order_id_dup = values[4];

            const shipping_address = values[5];
            const status = values[6];

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

$(document).ready(function () {
    const url = "/orders";

    function fetchJSONDataByStatus(status) {
        const queryUrl = `${url}?status_name=${status}`;
        console.log('Fetching data from:', queryUrl);
        $.ajax({
            url: queryUrl,
            type: 'GET',
            dataType: 'json',
            success: function (res) {
                fillTable(res);
                flash_message("Success");
            },
            error: function (error) {
                console.log('Error fetching data', error);
            }
        });
    }

    function fillTable(data) {
        const tbody = $('#search-results-body');

        tbody.empty();

        data.forEach(item => {
            const row = $('<tr>');
            const values = Object.values(item);
            console.log(values);
            const created_at = values[0];
            const customer_id = values[1];
            const order_id = values[2];
            const items = values[3];
            const order_id_dup = values[4];
            const shipping_address = values[5];
            const status = values[6];
    
            $.ajax({
                url: `/orders/${order_id}/items`,
                type: 'GET',
                dataType: 'json',
                success: function (response) {
                    const ids = response.map(item => item.id);
                    row.append($('<td>').text(ids));
                    console.log("RESPONSE");
                    console.log(response);
                },
                error: function (error) {
                    console.log('Error fetching data', error);
                }
            });

            row.append($('<td>').text(order_id));
            row.append($('<td>').text(customer_id));
            row.append($('<td>').text(created_at));
            row.append($('<td>').text(shipping_address));
            row.append($('<td>').text(status));

            tbody.append(row);
        });
    }

    function flash_message(message) {
        $("#orders_status").empty();
        $("#orders_status").append(message);
    }

    $('#order_status').change(function () {
        const selectedStatus = $(this).val();
        if (selectedStatus) {
            fetchJSONDataByStatus(selectedStatus);
        }
    });
});

$(document).ready(function () {
    const url = "/orders";

    var customerIdModal = document.getElementById("customerIdModal");
    var searchByCustomerIdBtn = document.getElementById("searchbycustomerid-btn");
    var closeCustomerIdModalBtn = document.getElementById("closeCustomerIdModal-btn");

    searchByCustomerIdBtn.onclick = function () {
        customerIdModal.style.display = "block";
    }

    closeCustomerIdModalBtn.onclick = function () {
        customerIdModal.style.display = "none";
    }

    window.onclick = function (event) {
        if (event.target == customerIdModal) {
            customerIdModal.style.display = "none";
        }
    }

    function fetchJSONDataByCustomerId(customer_id) {
        const queryUrl = `${url}?customer_id=${customer_id}`;
        console.log('Fetching data from:', queryUrl);
        $.ajax({
            url: queryUrl,
            type: 'GET',
            dataType: 'json',
            success: function (res) {
                if (res.length > 0) {
                    fillTable(res);
                    flash_message("Success");
                } else {
                    flash_message("404");
                }
            },
            error: function (res) {
                console.log('Error fetching data', error);
                flash_message(res.responseJSON.message);
            }
        });
    }

    function fillTable(data) {
        const tbody = $('#search-results-body');

        tbody.empty();

        data.forEach(item => {
            const row = $('<tr>');
            const values = Object.values(item);
            const created_at = values[0];
            const customer_id = values[1];
            const order_id = values[2];
            const shipping_address = values[5];
            const status = values[6];

            $.ajax({
                url: `/orders/${order_id}/items`,
                type: 'GET',
                dataType: 'json',
                success: function (response) {
                    const ids = response.map(item => item.id);
                    row.append($('<td>').text(ids));
                    console.log("RESPONSE");
                    console.log(response);
                },
                error: function (error) {
                    console.log('Error fetching data', error);
                }
            });

            row.append($('<td>').text(order_id));
            row.append($('<td>').text(customer_id));
            row.append($('<td>').text(created_at));
            row.append($('<td>').text(shipping_address));
            row.append($('<td>').text(status));

            tbody.append(row);
        });
    }

    function flash_message(message) {
        $("#orders_status").empty();
        $("#orders_status").append(message);
    }

    $("#customerIdForm").submit(function (event) {
        event.preventDefault();
        const customer_id = $('#orders_customer_id').val();
        if (customer_id) {
            fetchJSONDataByCustomerId(customer_id);
            customerIdModal.style.display = "none";
        }
    });
});

$(document).ready(function () {

    var modal = document.getElementById("updateOrderStatusModal");
    var btn = document.getElementById("changeorderstatus-btn");
    var span = document.getElementById("closeUpdateOrderStatusModal-btn");

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

    $("#updateOrderStatusForm").submit(function (event) {
        event.preventDefault();
        const orderId = $("#orders_id_update").val();
        const newStatus = $("#new_order_status").val();

        if (!orderId) {
            flash_message("Order ID is required");
            return;
        }

        const data = {
            "status": newStatus
        };

        $.ajax({
            type: "PUT",
            url: `/orders/${orderId}/status`,
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function (res) {
                flash_message("Success");
                modal.style.display = "none";
            },
            error: function (res) {
                flash_message(res.responseJSON.message);
            }
        });
    });

    function flash_message(message) {
        $("#orders_status").empty();
        $("#orders_status").append(message);
    }

});


var modal = document.getElementById("orderModal");
var updatemodal = document.getElementById("updateorderModal");
var deletemodal = document.getElementById("deleteOrderModal");



var btn = document.getElementById("createorder-btn");
var btn_update = document.getElementById("updateorder-btn");
var btn_delete = document.getElementById("deleteorder-btn");


var close_update = document.getElementById("updatecloseordermodal-btn")


var span = document.getElementsByClassName("close")[0];

var closeDelete = document.getElementById("closedeleteordermodal-btn");
var close_create = document.getElementById("closeordermodal-btn");



btn.onclick = function () {
    modal.style.display = "block";
}

close_create.onclick = function () {
    modal.style.display = "none";
}


window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

btn_update.onclick = function () {
    updatemodal.style.display = "block";
}

btn_delete.onclick = function () {
    deletemodal.style.display = "block";
}

// window.onclick = function (event) {
//     if (event.target == modal) {
//         updatemodal.style.display = "none";
//     }
// }

close_update.onclick = function () {
    updatemodal.style.display = "none";
}

closeDelete.onclick = function () {
    deletemodal.style.display = "none";
}
// UPDATE ORDER


function createRequestObject(array_ids, array_quantities, shippingAddress) {
    let items = [];
    for (let i = 0; i < array_ids.length; i++) {
        items.push({
            id: array_ids[i],
            quantity: array_quantities[i]
        });
    }

    return {
        items: items,
        shippingAddress: shippingAddress
    };
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

document.getElementById("updateorderForm").onsubmit = function (event) {
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

    var orderID = document.getElementById("orders_id").value;


    // Validate Item IDs
    var itemIds = document.getElementById("orders_update_item_ids").value;
    if (!itemIds) {
        document.getElementById("itemIdsError").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("itemIdsError").style.display = "none";
    }

    // Validate Item Quantities
    var itemQuantities = document.getElementById("orders_update_item_quantities").value;
    if (!itemQuantities) {
        document.getElementById("itemQuantitiesError").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("itemQuantitiesError").style.display = "none";
    }

    // Validate Shipping Address
    var shippingAddress = document.getElementById("orders_update_shipping_address").value;
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
            type: "PUT",
            url: `/orders/${orderID}`,
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

document.getElementById("orderIdForm").onsubmit = function (event) {
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

    // Validate Order ID
    isValid = true;
    var orderId = document.getElementById("orders_order_id").value;
    if (!orderId) {
        document.getElementById("orderIdsError").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("orderIdsError").style.display = "none";
    }

    // If all fields are valid, create JSON object
    if (isValid) {
        console.log(orderId);

        let ajax = $.ajax({
            type: "DELETE",
            url: `/orders/${orderId}`,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function (res, textStatus, xhr) {
            flash_message_create(res)
            console.log("RESULT: ");
            console.log(res);
            console.log(xhr.status);
            if (xhr.status == "204")
                $("#orders_status").text("Deleted Successfully (204)");
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


