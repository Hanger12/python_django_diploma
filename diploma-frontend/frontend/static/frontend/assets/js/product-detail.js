var mix = {
    computed: {
        tags() {
            if (!this.product?.tags) return []
            return this.product.tags
        }
    },
    methods: {
        changeCount(value) {
            this.count = this.count + value
            if (this.count < 1) this.count = 1
        },
        getProduct() {
            const productId = location.pathname.startsWith('/product/')
                ? Number(location.pathname.replace('/product/', '').replace('/', ''))
                : null
            this.getData(`/api/product/${productId}`).then(data => {
                this.product = {
                    ...this.product,
                    ...data
                }
                if (data.images.length)
                    this.activePhoto = 0
            }).catch(() => {
                this.product = {}
                console.warn('Ошибка при получении товара')
            })
        },
        // Метод для получения данных текущего авторизованного пользователя
        getCurrentUser() {
            this.getData('/api/current_user').then(user => {
                if (user)
                    this.currentUser = user;
                    this.review.author = user.username; // Автоматическое заполнение имени автора
                    this.review.email = user.email; // Автоматическое заполнение email
            }).catch(() => {
                console.warn('Ошибка при получении данных о текущем пользователе');
            });
        },
        submitReview() {
            this.postData(`/api/product/${this.product.id}/reviews`, {
                author: this.review.author,
                email: this.review.email,
                text: this.review.text,
                rate: this.review.rate
            }).then(({data}) => {
                this.product.reviews = data
                alert('Отзыв опубликован')
                this.review.author = ''
                this.review.email = ''
                this.review.text = ''
                this.review.rate = 5
            }).catch(() => {
                console.warn('Ошибка при публикации отзыва')
            })
        },
        setActivePhoto(index) {
            this.activePhoto = index
        }
    },
    mounted() {
        this.getProduct();
        this.getCurrentUser();
    },
    data() {
        return {
            product: {},
            activePhoto: 0,
            count: 1,
            review: {
                author: '',
                email: '',
                text: '',
                rate: 5
            },
            currentUser: null
        }
    },
}