# app/core/constants/i18n_texts.py
# FIX-103
class I18nKeys:
    """
    Botdagi barcha matnlar uchun kalitlar.
    Bu fayl loyiha matnlarini bir necha tilga moslashuvchan qiladi.
    """

    # --- Umumiy xabarlar ---
    WELCOME_MESSAGE = "welcome-message"
    LANGUAGE_CHANGED_MESSAGE = "language-changed-message"
    UNKNOWN_COMMAND_MESSAGE = "unknown-command-message"
    FUNCTIONALITY_IN_DEVELOPMENT = "functionality-in-development"
    ERROR_OCCURRED = "error-occurred"
    MAIN_MENU_MESSAGE = "main-menu-message"

    # --- Ovoz berish jarayoni uchun xabarlar ---
    ASK_PHONE_NUMBER = "ask-phone-number"
    PHONE_NUMBER_INVALID = "phone-number-invalid"
    ASK_CAPTCHA_RESULT = "ask-captcha-result"
    CAPTCHA_INVALID = "captcha-invalid"
    ASK_OTP_CODE = "ask-otp-code"
    OTP_INVALID = "otp-invalid"
    PHONE_ALREADY_USED = "phone-already-used"
    VOTE_SUCCESSFUL = "vote-successful"
    API_ERROR = "api-error"

    # --- Hisob va referal uchun xabarlar ---
    ACCOUNT_INFO_MESSAGE = "account-info-message"
    REFERRAL_INFO_MESSAGE = "referral-info-message"

    # --- Admin paneli xabarlari ---
    ADMIN_PANEL_MESSAGE = "admin-panel-message"
    STATS_MESSAGE = "stats-message"
    SEND_NOTIFICATION_MESSAGE = "send-notification-message"
    NOTIFICATION_SENT_MESSAGE = "notification-sent-message"

    # --- Boshqa xabarlar ---
    CANCEL_ACTION = "cancel-action"
    CONFIRM_ACTION = "confirm-action"
    HELP_MESSAGE = "help-message"

    # --- Referal bonus xabarlari ---
    REFERRAL_BONUS_NOTIFICATION = "referral-bonus-notification"
    REFERRAL_BONUS_CLAIMED = "referral-bonus-claimed"
    NEW_REFERRAL_NOTIFICATION = "new-referral-notification"
    
    # FIX-103: Bot buyruqlari uchun yangi kalitlar
    START_MESSAGE_COMMAND = "start-message-command"
    ACCOUNT_MESSAGE_COMMAND = "account-message-command"
    HELP_MESSAGE_COMMAND = "help-message-command"

    # FIX-102: help.py faylidagi matnlar uchun yangi kalitlar
    HELP_MAIN_TEXT = "help-main-text"
    BUTTON_SHOW_FAQ = "button-show-faq"
    FAQ_SECTION_TITLE = "faq-section-title"
    FAQ_NOT_FOUND = "faq-not-found"
    FAQ_NO_QUESTIONS = "faq-no-questions"
    BUTTON_BACK_TO_FAQ = "button-back-to-faq"
    FAQ_QUESTION_TEXT = "faq-question-text"
    FAQ_ANSWER_TEXT = "faq-answer-text"

    # FIX-102: withdrawal.py faylidagi matnlar uchun yangi kalitlar
    BUTTON_WITHDRAW = "button-withdraw"
    WITHDRAW_MIN_AMOUNT_ERROR = "withdraw-min-amount-error"
    ASK_CARD_NUMBER = "ask-card-number"
    INVALID_CARD_NUMBER = "invalid-card-number"
    ASK_AMOUNT = "ask-amount"
    INVALID_AMOUNT = "invalid-amount"
    INSUFFICIENT_FUNDS = "insufficient-funds"
    WITHDRAWAL_REQUEST_SENT = "withdrawal-request-sent"
    NEW_PAYMENT_REQUEST = "new-payment-request"
    PAYMENT_APPROVED_ADMIN = "payment-approved-admin"
    PAYMENT_REJECTED_ADMIN = "payment-rejected-admin"

    # FIX-102: payment_verification.py faylidagi matnlar uchun yangi kalitlar
    BUTTON_PENDING_WITHDRAWALS = "button-pending-withdrawals"
    NO_PENDING_WITHDRAWALS = "no-pending-withdrawals"
    PAYMENT_APPROVED_USER_NOTIFICATION = "payment-approved-user-notification"
    PAYMENT_REJECTED_USER_NOTIFICATION = "payment-rejected-user-notification"

    # FIX-102: messaging.py faylidagi matnlar uchun yangi kalitlar
    ASK_FOR_MESSAGE_CONTENT = "ask-for-message-content"
    MESSAGE_PREVIEW_AND_CONFIRMATION = "message-preview-and-confirmation"
    BROADCAST_STARTED = "broadcast-started"
    BROADCAST_FINISHED = "broadcast-finished"
    BROADCAST_CANCELLED = "broadcast-cancelled"
    BUTTON_CONFIRM_BROADCAST = "button-confirm-broadcast"
    BUTTON_CANCEL_BROADCAST = "button-cancel-broadcast"

    # FIX-106: Qo'lda ovoz berish uchun yangi kalitlar
    MANUAL_VOTING_LINK_NOT_SET = "manual-voting-link-not-set"
    MANUAL_VOTING_INSTRUCTIONS = "manual-voting-instructions"


    # Admin sozlamalari uchun yangi kalitlar
    SET_VOTING_MODE_NO_ARGS_ERROR = "set-voting-mode-no-args-error"
    SET_VOTING_MODE_INVALID_ERROR = "set-voting-mode-invalid-error"
    SET_VOTING_MODE_SUCCESS = "set-voting-mode-success"
    SET_VOTING_LINK_INVALID_ERROR = "set-voting-link-invalid-error"
    SET_VOTING_LINK_SUCCESS = "set-voting-link-success"
    CURRENT_SETTINGS_INFO = "current-settings-info"
    AUTO_DEFAULT = "auto-default"
    NOT_SET = "not-set"


    API_SERVER_ERROR = "api-server-error"

    # Hisob va pul yechish uchun yangi kalitlar
    WITHDRAWAL_CANCEL_ERROR = "withdrawal-cancel-error"
    WITHDRAWAL_CANCELLED_MESSAGE = "withdrawal-cancelled-message"
    BUTTON_CANCEL = "button-cancel"

    # Foydalanuvchini bloklash va blokdan chiqarish uchun xabarlar
    USER_BLOCKED_NOTIFICATION = "user-blocked-notification"
    USER_UNBLOCKED_NOTIFICATION = "user-unblocked-notification"

    BUTTON_VOTE_HISTORY = "button-vote-history"
    NO_VOTES_FOUND = "no-votes-found"


    ASK_PROJECT_ID = "ask-project-id"
    PROJECT_ID_INVALID = "project-id-invalid"

    VOTE_PREVIEW = "vote-preview"

    BUTTON_BACK = "button-back"

    VOTE_COOLDOWN = "vote-cooldown"

    OTP_RESENT_MESSAGE = "otp-resent-message"
    BUTTON_RESEND_OTP = "button-resend-otp"


    NO_PERMISSION = "no-permission"













# ----------------------------- 



