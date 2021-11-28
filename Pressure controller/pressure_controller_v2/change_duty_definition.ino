#define change_duty_definition \
template<typename pwm_type> void change_duty( \
  pwm_type& pwm_obj, uint32_t pwm_duty, uint32_t pwm_period \
  ){ \
  uint32_t duty=pwm_duty; \
  pwm_obj.set_duty(duty); \
}
change_duty_definition;
