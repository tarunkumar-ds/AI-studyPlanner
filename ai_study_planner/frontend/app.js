let step = 0;

const ctx = document.getElementById("combinedChart");

const chart = new Chart(ctx, {
    type: "line",
    data: {
        labels: [],
        datasets: [
            {
                label: "Productivity",
                data: [],
                borderColor: "black",
                tension: 0.3
            },
            {
                label: "Fatigue",
                data: [],
                borderColor: "gray",
                tension: 0.3
            }
        ]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});


async function predict() {

    document.getElementById("status").innerText = "Analyzing...";
    document.getElementById("study-plan").innerHTML = "";

    const payload = {
        study_hours: Number(document.getElementById("study").value),
        break_hours: Number(document.getElementById("break").value),
        sleep_hours: Number(document.getElementById("sleep").value),
        stress: Number(document.getElementById("stress").value),
        focus: Number(document.getElementById("focus").value)
    };

    try {

        const response = await fetch("https://ai-studyplanner-8.onrender.com", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        document.getElementById("burnout").innerText = data.burnout;
        document.getElementById("fatigue").innerText = data.fatigue;
        document.getElementById("productivity").innerText = data.productivity + " / 100";

        buildStudyPlan(data.burnout);
        updateChart(data.productivity, data.fatigue);

        document.getElementById("status").innerText = "";

    } catch {
        document.getElementById("status").innerText = "Backend not reachable.";
    }
}


function buildStudyPlan(level) {

    const plan = document.getElementById("study-plan");
    const title = document.getElementById("plan-title");

    let items = [];

    if (level === "High") {
        title.innerText = "High Burnout Plan";
        items = [
            "Study only 2–3 hours",
            "Break every 30 minutes",
            "Sleep 8–9 hours",
            "Light revision",
            "Take rest tomorrow"
        ];
    } else if (level === "Medium") {
        title.innerText = "Balanced Plan";
        items = [
            "Study 4–5 hours",
            "Break every 45 minutes",
            "Sleep 7–8 hours",
            "Mix easy + medium topics"
        ];
    } else {
        title.innerText = "Productive Plan";
        items = [
            "Study 6–8 hours",
            "Break every hour",
            "Sleep minimum 7 hours",
            "Focus on difficult topics"
        ];
    }

    items.forEach(t => {
        const li = document.createElement("li");
        li.innerText = t;
        plan.appendChild(li);
    });
}


function updateChart(productivity, fatigue) {

    step += 1;

    chart.data.labels.push(step);
    chart.data.datasets[0].data.push(productivity);
    chart.data.datasets[1].data.push(fatigue);

    chart.update();
}


