let ToastManager = {
    add_toast: function (message, type, delay=null) {
        let toast = $(
            `<div class="toast align-items-center fade show bg-${type}" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>`
        )
        $('#toasts').append(toast)
        if (delay !== null) {
            setTimeout(this.clear, delay, toast.get(0));
        }
    },
    success: function (message, delay=null) {
        this.add_toast(message, 'success', delay)
    },
    info: function (message, delay=null) {
        this.add_toast(message, 'info', delay)
    },
    warning: function (message, delay=null) {
        this.add_toast(message, 'warning', delay)
    },
    error: function (message, delay=null) {
        this.add_toast(message, 'danger', delay)
    },
    primary: function (message, delay=null) {
        this.add_toast(message, 'primary', delay)
    },
    secondary: function (message, delay=null) {
        this.add_toast(message, 'secondary', delay)
    },
    clear: function (item) {
        bootstrap.Toast.getOrCreateInstance(item).hide()
    },
    clearAll: function () {
        $('#toasts > div').each((_, item) => {
            this.clear(item)
        })
    }
}
