document.addEventListener("DOMContentLoaded", () => {
    const page = document.querySelector(".page");

    // fade in
    requestAnimationFrame(() => {
        page.classList.add("show");
    });

    // intercept link click
    document.querySelectorAll("a").forEach(link => {
        if (link.href && link.origin === location.origin) {
            link.addEventListener("click", e => {
                e.preventDefault();
                const url = link.href;

                page.classList.remove("show");

                setTimeout(() => {
                    window.location.href = url;
                }, 300);
            });
        }
    });
});
