const closeButtons = document.querySelectorAll(".close");

closeButtons.forEach(function(button) {
    button.addEventListener("click", () => {
        var alertBox = button.closest(".alert");
        alertBox.remove();  // Removes the alert element
    });
});
