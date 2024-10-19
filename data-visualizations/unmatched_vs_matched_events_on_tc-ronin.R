library(ggplot2)
library(scales)
library(lubridate)
library(dplyr)

df <- read.csv('../cross-chain-rules-validator/analysis/ronin-bridge/data/matched_and_unmatched_tc_withdrawals.csv')

df <- df %>% mutate(value_mil = value_usd/10^6)

df$date <- as.POSIXct(df$date, format="%Y-%m-%d %H:%M:%S")

df$interval <- floor_date(df$date, "6 hour")

df_matched <- df[df$matched == "True", ]

df_agg <- df_matched %>%
  group_by(interval) %>%
  summarise(total_count_matched = n(), value = sum(value_mil))

df_agg <- df_agg %>% mutate(matched = "Matched")

df_unmatched <- df[df$matched == "False", ]

df_agg_2 <- df_unmatched %>%
  group_by(interval) %>%
  summarise(total_count_unmatched = n(), value = sum(value_mil))

df_agg_2 <- df_agg_2 %>% mutate(matched = "Unmatched")

merged_df = merge(df_agg, df_agg_2, by="interval", all.x = TRUE)

merged_df$interval <- as.Date(merged_df$interval, format="%Y-%m-%d")

ggplot(merged_df, aes(x=interval, y=total_count_matched)) + 
  geom_point(aes(size=value.x, color=matched.x), alpha=0.6) +
  geom_point(aes(size=value.y, color=matched.y), alpha=0.6) +
  scale_size_continuous(range = c(2, 12), breaks=c(0.1, 5, 10, 50, 100), labels = c("$0.1M", "$5M", "$10M", "$50M", "$100M"), name="Transferred Value (USD)") +
  scale_color_manual(values=c("red", "royalblue3")) +
  scale_y_continuous(breaks = seq(0, 300, 50), limits = c(0, 300)) +
  scale_x_date(limits = as.Date(c("2022-01-01", "2022-04-01")), date_labels="%Y-%m-%d", date_breaks  ="1 month") +
  labs(title = "Matched vs. Unmatched Withdrawal Events in T (Ronin Bridge)",
       x = "Date",
       y = "Number of Events",
       color = "") +
  theme_minimal() +
  theme(
    plot.margin = unit(c(0, 0, 0, 0), "cm"),
    text = element_text(family = "serif"),
    axis.line = element_line(colour = "black"),
    panel.grid.major.y = element_line(color = 4,
                                      size = 0.1,
                                      linetype = 2),
    panel.grid.major.x = element_line(color = 4,
                                      size = 0.1,
                                      linetype = 2),
    plot.title = element_text(face = "bold", size = 15, hjust = 0.5, vjust=1),
    panel.grid.minor.x = element_blank(),
    panel.grid.minor.y = element_blank(),
    axis.title.y=element_text(size=14, face="bold"),
    axis.title.x=element_text(size=14, face="bold"),
    legend.title = element_text(face = "bold", size=14),
    legend.text = element_text(size = 13, family = "mono"),
    axis.title = element_text(size = 13), 
    axis.text = element_text(size = 13, face="bold"),
  ) 
