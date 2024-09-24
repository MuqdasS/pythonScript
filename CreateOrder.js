

function triggerOrderCreation() {

    var formContext = Xrm.Page;  // Get form context in Dynamics 365

    var contactId = formContext.data.entity.getId();  // Get the contact ID
    var ownerId = formContext.context.getUserId(); //get ownerId
    contactId = contactId.replace("{", "").replace("}", "");  // Clean up the contact ID by removing curly braces
    ownerId = ownerId.replace("{", "").replace("}", "");
    console.log(contactId);
    console.log(ownerId);

    if (contactId == "") {
        // Ensure contactId retrieval is complete before showing the notification
        setTimeout(function () {
            showNotification("Contact ID not found.", "error");
        }, 0);
        return;
    }

    var flowUrl = "https://prod-21.uksouth.logic.azure.com:443/workflows/29346c950e564dbcb2da2645728cd267/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=g13JuuRXmbRDmvynZY6tjYpzVKtUrzaKv4haZNm_VV4";

     var data = {
        "contactId": contactId,
        "userId": ownerId
    };
    console.log("Data being sent to Flow: ", data);

    setTimeout(function () {
        showNotification("Order is being created for the contact.", "info");
    }, 0);

    var req = new XMLHttpRequest();
    req.open("POST", flowUrl, true);
    req.setRequestHeader("Content-Type", "application/json");
    req.setRequestHeader("Accept", "application/json");

    // Handle the response
    req.onreadystatechange = function () {
        if (req.readyState === 4) {
            if (req.status === 200) {
                // Ensure the notification is displayed after the order creation starts
                console.log("Order is created successfully");
                setTimeout(function () {
                    showNotification("Order has been created successfully.", "success");
                }, 0);
            } else {
                // Ensure error notification doesn't interfere with other actions
                setTimeout(function () {
                    showNotification("Order creation failed: " + req.responseText, "error");
                }, 0);
            }
        }
    };

    // Send the request with the data object as JSON
    req.send(JSON.stringify(data));
}

// Function to show non-intrusive notifications
function showNotification(message, level) {
    var notificationOptions = {
        type: 2,  // Global notification
        level: level,  // Success, Error, or Warning
        message: message,
        showCloseButton: true
    };

    // Add the global notification asynchronously
    Xrm.App.addGlobalNotification(notificationOptions).then(
        function success(notificationId) {
            console.log("Notification ID: " + notificationId);
        },
        function error(error) {
            console.log("Error showing notification: " + error.message);
        }
    );
}


