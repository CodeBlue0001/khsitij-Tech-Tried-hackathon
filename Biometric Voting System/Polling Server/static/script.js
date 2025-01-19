$(document).ready(function () {
    $("#search-form").on("submit", function (e) {
        e.preventDefault();
        const voterId = $("#voter_id").val();

        // AJAX request to fetch voter data
        $.ajax({
            url: "/",
            method: "POST",
            data: { voter_id: voterId },
            success: function (response) {
                // Populate modal with voter data
                $("#voter-name").text(response.name);
                $("#voter-voter-id").text(response.voter_id);
                $("#voter-state").text(response.state);
                $("#voter-district").text(response.district);
                $("#voter-constitution").text(response.constitution);
                $("#voter-gender").text(response.gender);

                // Load image
                if (response.photo) {
                    const photoUrl = `/image/${response.photo_file_id}`;
                    $("#voter-photo").attr("src", photoUrl);
                } else {
                    $("#voter-photo").attr("src", "");
                }

                // Show modal
                $("#voter-modal").show();
            },
            error: function () {
                alert("Voter not found!");
            },
        });
    });

    // Close modal
    $(".close-button").on("click", function () {
        $("#voter-modal").hide();
    });
});
