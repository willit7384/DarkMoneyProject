document.addEventListener("DOMContentLoaded", () => {
    fetch("/api/nonprofits")
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector("#nonprofitTable tbody");
            data.forEach(org => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${org.EIN}</td>
                    <td>${org.Organization}</td>
                    <td>${org.TotalRevenue.toLocaleString()}</td>
                    <td>${org.GrantsPaid.toLocaleString()}</td>
                    <td>${org.AdminExpense.toLocaleString()}</td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(err => console.error("Error fetching data:", err));
});
