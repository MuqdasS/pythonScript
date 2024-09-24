function InventoryQuantity(){

    var flowURL = "https://prod-15.uksouth.logic.azure.com:443/workflows/fdc688c2223e4019909cf33ce993e58e/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=Vve_Xb4JakqOZ64hNhCuzo8Lqmh2ivaOdmD8Jrhy2s0"
    var page = Xrm.Page;

    var data = {
        "inventoryID" : "213213"
    }

    var req = new XMLHttpRequest();
    req.open("POST", flowURL, true);
    req.setRequestHeader("Content-Type", "application/json");
    req.setRequestHeader("Accept", "application/json");

    // Handle the response
    req.onreadystatechange = function () {
        if (req.readyState === 4) {
            if (req.status === 200) {
                // Ensure the notification is displayed after the order creation starts
                console.log("successfully");
                
            } else {
                // Ensure error notification doesn't interfere with other actions
                console.log("failed");
            }
        }
    };

    // Send the request with the data object as JSON
    req.send(JSON.stringify(data));
}