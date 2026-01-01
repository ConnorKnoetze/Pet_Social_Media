document.addEventListener('DOMContentLoaded', function() {
    const bioTextarea = document.getElementById('bio');
    const charCountDisplay = document.getElementById('char-count');
    const maxChars = 255;

    function updateCharCount() {
        const currentLength = bioTextarea.value.length;
        charCountDisplay.textContent = `${currentLength}/${maxChars} characters`;
    }

    bioTextarea.addEventListener('input', function() {
        if (this.value.length > maxChars) {
            this.value = this.value.substring(0, maxChars);
        }
        updateCharCount();
    });
    updateCharCount();
});