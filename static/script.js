document.addEventListener("DOMContentLoaded", function () {

    const fulfilmentOptions =
        document.querySelectorAll(
            'input[name="fulfilment_method"]'
        );

    const collectionSection =
        document.getElementById(
            "collection-section"
        );

    const deliverySection =
        document.getElementById(
            "delivery-section"
        );


    function updateFulfilmentDisplay() {

        const selected =
            document.querySelector(
                'input[name="fulfilment_method"]:checked'
            );

        if (!selected) {
            return;
        }


        if (selected.value === "Collection") {

            collectionSection.style.display = "block";

            deliverySection.style.display = "none";

        } else if (selected.value === "Delivery") {

            collectionSection.style.display = "none";

            deliverySection.style.display = "block";

        }

    }


    fulfilmentOptions.forEach(function (option) {

        option.addEventListener(
            "change",
            updateFulfilmentDisplay
        );

    });


    updateFulfilmentDisplay();

});