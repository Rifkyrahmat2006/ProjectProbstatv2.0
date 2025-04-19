document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[data-transition]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            
            document.body.classList.add('fade-out');
            
            setTimeout(() => {
                window.location.href = href;
            }, 300);
        });
    });

    // Handle CSV upload
    const csvForm = document.getElementById('csvDropzone');
    if (csvForm) {
        csvForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-success';
                    alertDiv.textContent = data.message;
                    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.card'));
                    
                    // Auto-refresh after 1 second
                    setTimeout(() => {
                        window.location.href = data.redirect;
                    }, 1000);
                } else {
                    // Show error message
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-danger';
                    alertDiv.textContent = data.message;
                    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.card'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-danger';
                alertDiv.textContent = 'Terjadi kesalahan saat mengunggah file';
                document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.card'));
            });
        });
    }
}); 